from shop.payment.payment_service import PaymentService
from shop.models import Order
from django.core.cache import cache
from django.conf import settings
import uuid
import requests
import json


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
                "amount": str(int(order.total_price)), 
                "currency": "Ar", 
                "descriptionText": f"Order {order.id}", 
                "requestDate": order.created_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"), 
                "debitParty": [{"key": "msisdn", "value": order.customer_phone}], 
                "creditParty": [{"key": "msisdn", "value": settings.MVOLA_PARTNER_MSISDN}], 
                "metadata": [{"key": "partnerName", "value": settings.MVOLA_PARTNER_NAME}], 
                "requestingOrganisationTransactionReference": transaction_ref,
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=10) 
            data = resp.json() 
            
            # Store transaction reference in order
            order.transaction_reference = transaction_ref
            order.transaction_id = data.get("transactionReference", "")
            order.save()
            
            print(f"[Mvola] Payment initiated for order {order.id}: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"[Mvola] API request failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
        except Exception as e:
            print(f"[Mvola] Unexpected error: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def check_status(self, order):
        """Check payment status from Mvola
        
        Args:
            order (Order): Order object to check status for
            
        Returns:
            str: Status string ('completed', 'failed', 'pending')
        """
        try:
            if not order.transaction_reference:
                return "pending"
            
            # In production, you would query Mvola API for actual status
            # For now, return based on what callback has set
            # The actual status is set by handle_callback() when Mvola sends the webhook
            
            # Fetch fresh from DB to get latest status
            order.refresh_from_db()
            return order.status
            
        except Exception as e:
            print(f"[Mvola] Status check failed: {str(e)}")
            return "failed"

    def handle_callback(self, data):
        """Handle Mvola payment callback webhook
        
        Args:
            data (dict): Callback data from Mvola containing transaction status
        """
        try:
            transaction_ref = data.get("requestingOrganisationTransactionReference")
            transaction_status = data.get("transactionStatus", "").lower()
            
            # Find order by transaction reference
            try:
                order = Order.objects.get(transaction_reference=transaction_ref)
            except Order.DoesNotExist:
                print(f"[Mvola] Order not found for transaction: {transaction_ref}")
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
            order.status = new_status
            order.transaction_id = data.get("transactionReference", order.transaction_id)
            order.save()
            
            print(f"[Mvola] Callback processed - Order {order.id} status: {new_status}")
            
        except Exception as e:
            print(f"[Mvola] Callback handling failed: {str(e)}")

    def _get_mvola_token(self):
        """Get or fetch new Mvola API token
        
        Returns:
            str: Bearer token for Mvola API
        """
        token = cache.get("mvola_token")
        if token:
            return token

        # Fetch new token from Mvola
        try:
            url = f"{settings.MVOLA_BASE_URL}/token"
            auth = (settings.MVOLA_CLIENT_ID, settings.MVOLA_CLIENT_SECRET)
            data = {"grant_type": "client_credentials"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            resp = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)
            resp.raise_for_status()
            
            token = resp.json()["access_token"]
            
            # Cache token for 55 minutes (tokens usually valid 1 hour)
            cache.set("mvola_token", token, timeout=3300)
            print("[Mvola] New token obtained and cached")
            return token
            
        except Exception as e:
            print(f"[Mvola] Token fetch failed: {str(e)}")
            raise Exception(f"Failed to obtain Mvola token: {str(e)}")