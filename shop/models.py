from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.urls import reverse

#Category model to classify biscuits
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

#Product model to represent biscuits in the shop
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    image = CloudinaryField('image', blank=True, null=True)
    
    class Meta:
        ordering = ['-id']
    
    def get_absolute_url(self):
        return reverse('product-detail', args=[self.id]) #type: ignore

    def __str__(self):
        return self.name

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    customer_phone = models.CharField(max_length=10, null=True, blank=True)
    customer_address = models.CharField(max_length=200, null=True, blank=True)
    
    # Payment transaction tracking
    transaction_reference = models.CharField(max_length=255, null=True, blank=True, unique=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self) -> str:
        return f"Order of {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Order item: {self.product} - order: {self.order}"
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)