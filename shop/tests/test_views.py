from django.urls import reverse
from shop.tests.test_base_setup import ShopTestBase

class GlobalContextTestCase(ShopTestBase):
    """Base test case to check for global context variables in views."""
    
    def assertGlobalContextPresent(self, response):
        """Check if global context variables are present in the response context."""
        expected_keys = [
            'cart', 'cart_count', 'cart_total_price',
            'wishlist', 'wishlist_count'
        ]
        for key in expected_keys:
            self.assertIn(key, response.context, f"La clé '{key}' manque dans le contexte de la vue.")

class ProductViewTest(GlobalContextTestCase):
    """Test cases for Product views

    Args:
        TestCase (_type_): _Django TestCase class
    """
    
    def test_home_view(self):
        """Test the home view
        """
        response = self.client.get(reverse('home'))         #type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/home.html')
        self.assertGlobalContextPresent(response)
        
    def test_toggle_wishlist_updates_context(self):
        """Test that toggling the wishlist updates global context variables
        """
        response = self.client.get(reverse('home'))  #type: ignore
        self.assertEqual(response.context['wishlist_count'], 0)
        
        toggle_wishlist_url = reverse('toggle-favorite', args=[self.product.id])  #type: ignore
        response = self.client.post(toggle_wishlist_url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertGlobalContextPresent(response)
        self.assertEqual(response.context['wishlist_count'], 1)
        
    def test_product_detail_view_context(self):
        """Test the product detail view for global context variables
        """
        response = self.client.get(reverse('product-detail', args=[self.product.id]))  #type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')
        self.assertGlobalContextPresent(response)
        
    def test_product_list_view_context(self):
        """Test the product list view for global context variables
        """
        response = self.client.get(reverse('product-list'))  #type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/products.html')
        self.assertIn('products', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('current_category', response.context)
        
class ShoppingViewsTest(GlobalContextTestCase):
    """Test cases for Shopping related views
    """
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.raw_pasword)
    
    def test_cart_view_context(self):
        """Test the cart view for global context variables
        """
        response = self.client.get(reverse('cart'))  #type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')
        self.assertIn('cart_items', response.context)
        self.assertIn('cart_total', response.context)
        
    def test_add_to_cart_updates_context(self):
        """Test that adding a product to the cart updates global context variables
        """
        response = self.client.get(reverse('home'))  #type: ignore
        self.assertEqual(response.context['cart_count'], 0)
        self.assertEqual(response.context['cart_total_price'], 0)
        
        add_to_cart_url = reverse('add-to-cart', args=[self.product.id])  #type: ignore
        response = self.client.post(add_to_cart_url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertGlobalContextPresent(response)
        self.assertEqual(response.context['cart_count'], 1)
        self.assertEqual(response.context['cart_total_price'], self.product.price)
        
    def test_remove_from_cart_updates_context(self):
        """Test that removing a product from the cart updates global context variables
        """
        add_to_cart_url = reverse('add-to-cart', args=[self.product.id])  #type: ignore
        self.client.post(add_to_cart_url, follow=True)
        
        response = self.client.get(reverse('home'))  #type: ignore
        self.assertEqual(response.context['cart_count'], 1)
        
        remove_from_cart_url = reverse('remove-from-cart', args=[self.product.id])  #type: ignore
        response = self.client.post(remove_from_cart_url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertGlobalContextPresent(response)
        self.assertEqual(response.context['cart_count'], 0)
        self.assertEqual(response.context['cart_total_price'], 0)
        
    def test_substract_item_qty_from_cart_updates_context(self):
        """Test that subtracting item quantity from the cart updates global context variables
        """
        add_to_cart_url = reverse('add-to-cart', args=[self.product.id])  #type: ignore
        self.client.post(add_to_cart_url, follow=True)
        self.client.post(add_to_cart_url, follow=True)  # Add twice to have quantity 2
        
        response = self.client.get(reverse('home'))  #type: ignore
        self.assertEqual(response.context['cart_count'], 2)
        
        substract_from_cart_url = reverse('substract-from-cart', args=[self.product.id])  #type: ignore
        response = self.client.post(substract_from_cart_url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertGlobalContextPresent(response)
        self.assertEqual(response.context['cart_count'], 1)
        self.assertEqual(response.context['cart_total_price'], self.product.price)
        
class PaymentViewsTest(GlobalContextTestCase):
    """Test cases for Payment related views
    """
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.raw_pasword)
        session = self.client.session
        session['cart'] = self.cart_data
        session.save()
        
    
    def test_checkout_view_context(self):
        """Test the checkout view for global context variables
        """
        response = self.client.get(reverse('checkout'))  #type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/checkout_success.html')
        self.assertIn('cart_items', response.context)
        self.assertIn('cart_total_price', response.context)
        self.assertGlobalContextPresent(response)










