from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from shop.models import Product, Category, WishlistItem, Order, OrderItem, CartItem
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from shop.tests.test_base_setup import ShopTestBase


class ProductModelTest(ShopTestBase):
    """test cases for Product model

    Args:
        TestCase (_type_): _Django TestCase class
    """

    def test_product_creation(self):
        """test product creation
        """
        self.assertEqual(self.product.name, "Petit Beurre")
        self.assertEqual(self.product.category.name, "Biscuits")
        self.assertEqual(self.product.price, 1000.00)
        self.assertEqual(self.product.stock, 100)
        
    def test_product_price(self):
        self.assertEqual(self.product.price, 1000.00)
        
    def test_stock_can_not_be_negative(self):
        """test that stock cannot be negative"""
        self.product.stock = -1
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_get_absolute_url(self):
        """test get_absolute_url method
        """
        url = self.product.get_absolute_url()
        expected_url = reverse('product-detail', args=[self.product.id]) #type: ignore
        self.assertEqual(url, expected_url)
        
class ShoppingModelsTest(ShopTestBase):

    def test_cart_item_uniqueness(self):
        """Vérifie qu'on ne peut pas avoir deux entrées pour le même couple user/produit"""
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        
        with self.assertRaises(IntegrityError):
            # Tenter de créer exactement le même item doit échouer
            CartItem.objects.create(user=self.user, product=self.product, quantity=2)

    def test_wishlist_item_uniqueness(self):
        """Vérifie l'unicité dans la liste de souhaits"""
        WishlistItem.objects.create(user=self.user, product=self.product)
        
        with self.assertRaises(IntegrityError):
            WishlistItem.objects.create(user=self.user, product=self.product)
            
    def test_order_creation_with_items(self):
            order = Order.objects.create(
                user=self.user,
                total_price=15.00,
                status='pending',
                customer_phone="0102030405"
            )
            
            order_item = OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=3,
                price=self.product.price
            )
            
            # Check that order and order item are created correctly and the related name items works
            self.assertEqual(order.items.count(), 1) # type: ignore
            self.assertEqual(order.items.first().product.name, 'Petit Beurre') #type: ignore
            self.assertEqual(str(order), f"Order of {self.user}")
            
    def test_order_item_price_persistence(self):
        # product created with initial price
        product = Product.objects.create(name='Biscuits Vanille', price=2.50, stock=10, category=self.category)
        
        # order created with that product
        order = Order.objects.create(user=self.user, total_price=2.50)
        order_item = OrderItem.objects.create(
            order=order, 
            product=product, 
            quantity=1, 
            price=product.price
        )

        # Price changed on the product
        product.price = 5.00 #type: ignore
        product.save()

        # Verification : the price in the order item should remain unchanged
        order_item.refresh_from_db()
        self.assertEqual(order_item.price, 2.50)
        self.assertNotEqual(order_item.price, product.price)

