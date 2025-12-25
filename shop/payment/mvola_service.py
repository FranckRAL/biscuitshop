from shop.payment.payment_service import PaymentService
from shop.models import Order
from django.core.cache import cache
from django.conf import settings
import uuid
import requests
import json
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
            token = self._get_mvola_token()
            transaction_ref = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
            
            headers = { 
                "Authorization": f"Bearer {token}", 
                "Version": "1.0", 
                "X-CorrelationID": str(uuid.uuid4()), 
                "UserLanguage": "FR", 
                "UserAccountIdentifier": f"msisdn;{settings.MVOLA_PARTNER_MSISDN}", 
                "partnerName": settings.MVOLA_PARTNER_NAME, 
                "Content-Type": "application/json", 
                "X-Callback-URL": request.build_absolute_uri("/mvola/callback/"), 
                "Cache-Control": "no-cache",
            }
            
            payload = { 
                "amount": str(int((order.total_price + 1000))), 
                "currency": "Ar", 
                "descriptionText": f"Order {order.id}", 
                "requestDate": order.created_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"), 
                "debitParty": [{"key": "msisdn", "value": order.customer_phone}], 
                "creditParty": [{"key": "msisdn", "value": settings.MVOLA_PARTNER_MSISDN}], 
                "metadata": [{"key": "partnerName", "value": settings.MVOLA_PARTNER_NAME}], 
                "requestingOrganisationTransactionReference": transaction_ref,
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # Store transaction reference in order
            order.transaction_reference = transaction_ref
            order.transaction_id = data.get("transactionReference", "")
            order.save()
            
            logger.info(f"[Mvola] Payment initiated for order {order.id}: {data}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"[Mvola] Request timeout for order {order.id}")
            return {"status": "failed", "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            logger.error(f"[Mvola] API request failed for order {order.id}: {str(e)}")
            return {"status": "failed", "error": str(e)}
        except ValueError as e:
            logger.error(f"[Mvola] Validation error for order {order.id}: {str(e)}")
            return {"status": "failed", "error": str(e)}
        except Exception as e:
            logger.error(f"[Mvola] Unexpected error for order {order.id}: {str(e)}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    def check_status(self, order):
        """Check payment status from Mvola API
        
        This method queries the Mvola API for the current transaction status
        instead of just returning the cached status in the database.
        
        Args:
            order (Order): Order object to check status for
            
        Returns:
            str: Status string ('completed', 'failed', 'pending')
        """
        try:
            if not order.transaction_reference:
                logger.warning(f"No transaction reference for order {order.id}")
                return "pending"
            
            # Query Mvola API for actual transaction status
            url = f"{settings.MVOLA_API_URL}/{order.transaction_reference}"
            token = self._get_mvola_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Version": "1.0",
                "X-CorrelationID": str(uuid.uuid4()),
                "UserLanguage": "FR",
                "UserAccountIdentifier": f"msisdn;{settings.MVOLA_PARTNER_MSISDN}",
                "Content-Type": "application/json",
            }
            
            # Make GET request to check transaction status
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            transaction_status = data.get("transactionStatus", "").lower()
            
            # Map Mvola status to our internal status
            status_map = {
                "completed": "completed",
                "success": "completed",
                "successful": "completed",
                "failed": "failed",
                "cancelled": "cancelled",
                "pending": "pending",
            }
            
            status = status_map.get(transaction_status, "pending")
            logger.info(f"Order {order.id} status from Mvola API: {status}")
            
            return status
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout checking status for order {order.id}")
            return "pending"
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for order {order.id}: {str(e)}")
            # Return database status as fallback
            return order.status
        except Exception as e:
            logger.error(f"Unexpected error checking status for order {order.id}: {str(e)}")
            # Return database status as fallback
            return order.status

    def handle_callback(self, data):
        """Handle Mvola payment callback webhook
        
        Args:
            data (dict): Callback data from Mvola containing transaction status
        """
        try:
            transaction_ref = data.get("requestingOrganisationTransactionReference")
            transaction_status = data.get("transactionStatus", "").lower()
            
            if not transaction_ref:
                logger.error("[Mvola] Missing transaction reference in callback")
                return
            
            # Find order by transaction reference
            try:
                order = Order.objects.get(transaction_reference=transaction_ref)
            except Order.DoesNotExist:
                logger.error(f"[Mvola] Order not found for transaction: {transaction_ref}")
                return
            
            # Map Mvola status to our status choices
            status_map = {
                "completed": "completed",
                "success": "completed",
                "successful": "completed",
                "failed": "failed",
                "cancelled": "cancelled",
                "pending": "pending",
            }
            
            new_status = status_map.get(transaction_status, "failed")
            
            # Only update if status has changed to prevent duplicate processing
            if order.status != new_status:
                order.status = new_status
                order.transaction_id = data.get("transactionReference", order.transaction_id)
                order.save()
                logger.info(f"[Mvola] Order {order.id} status updated from {order.status} to {new_status}")
            else:
                logger.info(f"[Mvola] Order {order.id} already has status: {new_status}")
            
        except Exception as e:
            logger.error(f"[Mvola] Callback handling failed: {str(e)}", exc_info=True)

    def _get_mvola_token(self):
        """Get or fetch new Mvola API token
        
        Returns:
            str: Bearer token for Mvola API
            
        Raises:
            Exception: If token fetch fails
        """
        token = cache.get("mvola_token")
        if token:
            logger.debug("Using cached Mvola token")
            return token

        # Fetch new token from Mvola
        try:
            url = f"{settings.MVOLA_ACCESS_TOKEN_ENDPOINT}"
            auth = (settings.MVOLA_CLIENT_ID, settings.MVOLA_SECRET_KEY)
            data = {"grant_type": "client_credentials"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            resp = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)
            resp.raise_for_status()
            
            token = resp.json()["access_token"]
            
            # Cache token for 55 minutes (tokens usually valid 1 hour)
            cache.set("mvola_token", token, timeout=3300)
            logger.info("[Mvola] New token obtained and cached")
            return token
            
        except requests.exceptions.Timeout:
            logger.error("[Mvola] Token request timeout")
            raise Exception("Failed to obtain Mvola token: Request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"[Mvola] Token request failed: {str(e)}")
            raise Exception(f"Failed to obtain Mvola token: {str(e)}")
        except KeyError:
            logger.error("[Mvola] Invalid token response format")
            raise Exception("Failed to obtain Mvola token: Invalid response format")
        except Exception as e:
            logger.error(f"[Mvola] Unexpected error fetching token: {str(e)}")
            raise Exception(f"Failed to obtain Mvola token: {str(e)}")