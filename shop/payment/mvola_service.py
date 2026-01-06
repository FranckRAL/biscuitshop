from shop.payment.payment_service import PaymentService
from shop.models import Order
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
import uuid
import requests
import logging

logger = logging.getLogger(__name__)


class MvolaPaymentService(PaymentService):
    """Mvola payment service implementation for Madagascar mobile money"""
    
    def initiate_payment(self, request, order):
        """Initialize payment with Mvola API
        
        Args:
            request (Request): Django request object
            order (Order): Order object to process payment for
            
        Returns:
            dict: Response from Mvola API containing transaction reference
        """
        try:
            # Validate required fields
            if not order.customer_phone:
                raise ValueError("Customer phone number is required for Mvola payment")
            
            url = settings.MVOLA_API_URL
            logger.debug(f"[Mvola] API URL: {url}")
            
            # Validate URL
            if not url or not url.startswith('https://'):
                raise ValueError(f"Invalid API URL: {url}. Check MVOLA_API_URL in settings.")
            
            token = self._get_mvola_token()
            transaction_ref = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "Version": "1.0",
                "X-CorrelationID": str(uuid.uuid4()),
                "UserLanguage": "MG",
                "partnerName": settings.MVOLA_PARTNER_NAME.strip(),
                "X-Callback-URL": request.build_absolute_uri(reverse('mvola_callback')),
                "UseraccountIdentifier": f"msisdn;{settings.MVOLA_PARTNER_MSISDN}",
                "Cache-Control": "no-cache",
            }
            
            payload = {
                "amount": str(int(order.total_price + 1000)),
                "currency": "Ar",
                "descriptionText": f"Order {order.id}",
                "requestDate": order.created_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "debitParty": [{"key": "msisdn", "value": order.customer_phone}],
                "creditParty": [{"key": "msisdn", "value": settings.MVOLA_PARTNER_MSISDN}],
                "metadata": [{"key": "partnerName", "value": settings.MVOLA_PARTNER_NAME}],
                "requestingOrganisationTransactionReference": transaction_ref,
            }
            
            logger.info(f"[Mvola] Initiating payment for order {order.id}")
            
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            logger.debug(f"[Mvola] Response status: {resp.status_code}")
            
            resp.raise_for_status()
            data = resp.json()
            
            # Store transaction reference in order
            order.transaction_reference = transaction_ref
            order.transaction_id = data.get("serverCorrelationId", "")
            order.save()
            
            logger.info(f"[Mvola] Payment initiated for order {order.id}: status={data.get('status')}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"[Mvola] Request timeout for order {order.id}")
            raise
        except requests.exceptions.RequestException as e:
            error_msg = e.response.text if hasattr(e, 'response') and e.response else str(e)
            logger.error(f"[Mvola] API request failed: {error_msg}")
            raise
        except Exception as e:
            logger.error(f"[Mvola] Unexpected error: {str(e)}", exc_info=True)
            raise

    def check_status(self, order):
        """Check payment status from Mvola API
        
        Args:
            order (Order): Order object to check status for
            
        Returns:
            dict: Status information {'status': 'pending|completed|failed', 'order_status': 'pending|completed|failed'}
        """
        if not order.transaction_id:
            logger.warning(f"[Mvola] No transaction_id for order {order.id}")
            return {"status": "pending", "order_status": "pending"}
        
        url = f"{settings.MVOLA_API_URL}/status/{order.transaction_id}"
        
        try:
            token = self._get_mvola_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Version": "1.0",
                "X-CorrelationID": str(uuid.uuid4()),
                "UserLanguage": "MG",
                "partnerName": settings.MVOLA_PARTNER_NAME.strip(),
                "UseraccountIdentifier": f"msisdn;{settings.MVOLA_PARTNER_MSISDN}",
                "Cache-Control": "no-cache",
            }
            
            logger.debug(f"[Mvola] Checking status for order {order.id}")
            
            resp = requests.get(url, headers=headers, timeout=10)
            logger.debug(f"[Mvola] Status response: {resp.status_code}")
            
            resp.raise_for_status()
            data = resp.json()
            
            mvola_status = data.get("status", "pending")
            logger.info(f"[Mvola] Order {order.id} mvola_status: {mvola_status}")
            
            # Map Mvola status to order status
            if mvola_status == "completed":
                order_status = "completed"
                # Update order in database
                order.status = order_status
                order.save()
                logger.info(f"[Mvola] Order {order.id} marked as completed")
            elif mvola_status == "failed":
                order_status = "failed"
                order.status = order_status
                order.save()
                logger.info(f"[Mvola] Order {order.id} marked as failed")
            else:
                order_status = "pending"
            
            return {
                "status": mvola_status,
                "order_status": order_status,
                "message": data.get("message", "")
            }
        
        except Exception as e:
            logger.error(f"[Mvola] Failed to check status: {str(e)}")
            return {"status": "pending", "order_status": "pending", "error": str(e)}

    def handle_callback(self, data):
        """Handle Mvola payment callback webhook
        
        Args:
            data (dict): Callback data from Mvola
            
        Returns:
            dict: Response for callback
        """
        transaction_ref = data.get("requestingOrganisationTransactionReference")
        transaction_status = data.get("transactionStatus")
        
        logger.info(f"[Mvola] Processing callback for {transaction_ref}: {transaction_status}")
        
        try:
            order = Order.objects.get(transaction_reference=transaction_ref)
        except Order.DoesNotExist:
            logger.error(f"[Mvola] Order not found for reference {transaction_ref}")
            return {"status": "error", "message": "Order not found"}
        
        # Prevent duplicate processing - check if already processed
        if order.status in ['completed', 'failed']:
            logger.warning(f"[Mvola] Order {order.id} already processed with status {order.status}")#type: ignore
            return {"status": "success", "message": "Already processed"}
        
        try:
            # Map Mvola status to order status
            new_status = "completed" if transaction_status == "completed" else "failed"
            
            order.status = new_status
            order.save()
            
            logger.info(f"[Mvola] Order {order.id} updated to {new_status}") #type: ignore
            
            return {
                "status": "success",
                "order_id": order.id, #type: ignore
                "new_status": new_status,
            }
        
        except Exception as e:
            logger.error(f"[Mvola] Error processing callback: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _get_mvola_token(self):
        """Get or fetch new Mvola API token
        
        Returns:
            str: Bearer token for Mvola API
            
        Raises:
            Exception: If token fetch fails
        """
        token = cache.get("mvola_token")
        if token:
            logger.debug("[Mvola] Using cached token")
            return token

        try:
            url = settings.MVOLA_ACCESS_TOKEN_ENDPOINT
            auth = (settings.MVOLA_CLIENT_ID, settings.MVOLA_SECRET_KEY)
            data = {
                "grant_type": "client_credentials",
                "scope": settings.MVOLA_API_SCOPE,
            }
            
            logger.debug(f"[Mvola] Requesting new token")
            
            resp = requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=auth,
                timeout=10
            )
            
            resp.raise_for_status()
            
            resp_data = resp.json()
            token = resp_data.get("access_token")
            
            if not token:
                raise KeyError("access_token not in response")
            
            # Cache for 55 minutes (tokens usually valid 1 hour)
            cache.set("mvola_token", token, timeout=3300)
            logger.info("[Mvola] New token obtained and cached")
            return token
            
        except Exception as e:
            logger.error(f"[Mvola] Failed to obtain token: {str(e)}", exc_info=True)
            raise Exception(f"Failed to obtain Mvola token: {str(e)}")