from django.urls import reverse
from decimal import Decimal

from unittest.mock import patch
import json
from shop.tests.test_base_setup import ShopTestBase


class CheckoutViewTests(ShopTestBase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.raw_pasword)
        
        session = self.client.session
        session['cart'] = self.cart_data
        session.save()
        


    def test_checkout_creates_order_and_items(self):
        from shop.models import Order
        response = self.client.post(
            reverse("checkout"),
            {
                "payment_method": "cod",  # Cash on Delivery pour tester la logique simple
                "wallet_number": "",
            },
        )

        # Vérification
        order = Order.objects.latest('id')
        self.assertEqual(order.total_price, Decimal("5000.00"))                     # 5 articles à 1000.00 chacun
        self.assertEqual(order.items.count(), 1)                                    # type: ignore
        self.assertRedirects(response, reverse("order_success", args=[order.id]))   # type: ignore

    @patch("shop.payment.mvola_service.MvolaPaymentService.initiate_payment")
    def test_process_payment_mvola_redirection(self, mock_initiate):
        from shop.models import Order
        order = Order.objects.create(
            user=self.user, total_price=10000, payment_method="mvola"
        )
        
        mock_initiate.return_value = {"notificationMethod": "callback"}

        response = self.client.get(reverse("process_payment", args=[order.id]))  # type: ignore

        self.assertRedirects(response, reverse("order_waiting", args=[order.id]))  # type: ignore
 
        self.assertTrue(mock_initiate.called)

    def test_mvola_callback_updates_order_status(self):
        from shop.models import Order
        order = Order.objects.create(
            user=self.user,
            total_price=10000,
            status="pending",
            transaction_reference="REF-123",
        )

        # Données envoyées par Mvola
        callback_data = {
            "requestingOrganisationTransactionReference": "REF-123",
            "transactionStatus": "completed",
            "serverCorrelationId": "12345",
        }

        # On envoie un POST JSON au callback
        response = self.client.post(
            reverse("mvola_callback"),
            data=json.dumps(callback_data),
            content_type="application/json",
        )

        # On rafraîchit la commande et on vérifie le statut
        order.refresh_from_db()
        self.assertEqual(order.status, "completed")
        self.assertEqual(response.status_code, 200)


class PaymentAjaxTests(ShopTestBase):
    def setUp(self):
        super().setUp()
        from shop.models import Order
        self.client.login(username=self.user.username, password=self.raw_pasword)
        self.order = Order.objects.create(
            user=self.user,
            total_price=10000,
            status='pending',
            payment_method='mvola',
        )

    def test_check_payment_status_completed(self):
        """Check AJAX redirects on completed status"""
        # On simule le passage au statut complété
        self.order.status = "completed"
        self.order.save()

        response = self.client.get(reverse("check_payment_status", args=[self.order.id]))  # type: ignore

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertIn("redirect_url", data)
        self.assertEqual(data["redirect_url"], reverse("order_success", args=[self.order.id]))  # type: ignore

    @patch("shop.payment.mvola_service.MvolaPaymentService.check_status")
    def test_check_payment_status_pending(self, mock_check):
        """Check AJAX returns pending status from Mvola"""
        mock_check.return_value = {
            "status": "pending",
            "order_status": "pending",
            "message": "Waiting for payment confirmation",
        }

        response = self.client.get(reverse("check_payment_status", args=[self.order.id]))  # type: ignore

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_check.called)
        self.assertEqual(response.json()["status"], "pending")

    @patch("shop.payment.mvola_service.MvolaPaymentService.check_status")
    def test_check_payment_status_failed(self, mock_check):
        """Check AJAX returns failed status from Mvola"""
        mock_check.return_value = {
            "status": "failed",
            "order_status": "failed",
            "message": "Payment failed. Please try again.",
        }

        response = self.client.get(reverse("check_payment_status", args=[self.order.id]))  # type: ignore

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["message"], "Payment failed. Please try again.")
