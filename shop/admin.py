from django.contrib import admin
from .models import Category, Product, CustomerProfile, Order, OrderItem, CartItem, WishlistItem

#global admin
admin.site.site_title = "Biscuit Shop Admin"
admin.site.site_header = "Biscuit Shop Administration"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_editable = ('description',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    list_editable = ('price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    # readonly_fields = ('updated_at',)
    
    # def updated_at(self, obj):
    #     return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    
    # updated_at.short_description = 'Updated At'
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__name')