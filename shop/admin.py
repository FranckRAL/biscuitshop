from django.contrib import admin
from .models import Category, Product, CustomerProfile, Order, OrderItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CustomerProfile)
admin.site.register(Order)
admin.site.register(OrderItem)