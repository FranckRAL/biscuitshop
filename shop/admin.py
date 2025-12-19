from django.contrib import admin
from .models import Category, Product, CustomerProfile, Order, OrderItem, CartItem, WishlistItem

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CustomerProfile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(WishlistItem)