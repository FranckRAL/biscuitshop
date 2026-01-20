from django.test import TestCase
from django.urls import reverse
from shop.models import Category, Product, Order
from decimal import Decimal
from django.contrib.auth.models import User

class ShopTestBase(TestCase):
    def setUp(self):
        self.raw_pasword = 'Activation6421'
        self.username = 'tester'
        self.user = User.objects.create_user(username='tester', password=self.raw_pasword)
        
        self.category = Category.objects.create(
            name="Biscuits"
        )
        
        self.product = Product.objects.create(
            name='Petit Beurre',
            price=Decimal('1000.00'),
            stock=100,
            category=self.category
        )
        
        self.cart_data = {
            str(self.product.id): {                             #type: ignore
                'product_id': self.product.id,                  #type: ignore
                'name': self.product.name,
                'price': str(self.product.price),
                'quantity': 5,
            }
        }
        
        