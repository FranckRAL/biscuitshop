from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Category, Product, CustomerProfile, Order, OrderItem, CartItem, WishlistItem
from django.http import HttpResponse
from django.db.models import Sum
import csv


class BiscuitAdminSite(admin.AdminSite):
    site_header = "Administration Biscuit Shop"

    def each_context(self, request):
        context = super().each_context(request)
        
        total_sales = Order.objects.filter(status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
        order_count = Order.objects.count()

        context['stats_total_sales'] = total_sales
        context['stats_order_count'] = order_count
        
        return context
    
    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        for app in app_list:
            if app['app_label'] == 'shop':
                ordering = {
                    'Order': 1,
                    'Product': 2,
                    'Category': 3,
                    'CustomerProfile': 4,
                }
                app['models'].sort(key=lambda x: ordering.get(x['object_name'], 99))

        return app_list

admin_site = BiscuitAdminSite(name='myadmin')

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'price', 'stock')
    
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Tranche de prix' # Le titre affiché au-dessus du filtre
    parameter_name = 'price_range' # Le nom dans l'URL (?price_range=...)

    # 1. On définit les options cliquables
    def lookups(self, request, model_admin):
        return (
            ('low', 'Moins de 1Ar'),
            ('mid', 'Entre 1Ar et 5Ar'),
            ('high', 'Plus de 5Ar'),
        )

    # 2. On définit la logique SQL pour chaque option
    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=1)
        if self.value() == 'mid':
            return queryset.filter(price__gte=1, price__lte=5)
        if self.value() == 'high':
            return queryset.filter(price__gt=5)

def export_as_csv(modeladmin, request, queryset):
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_biscuit_shop.csv"'
    
    writer = csv.writer(response)
    
    fields = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(fields)
    
    # 2. Écrire les données pour chaque objet sélectionné
    for obj in queryset:
        row = [getattr(obj, field) for field in fields]
        writer.writerow(row)
        
    return response

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_editable = ('description',)
    search_fields = ('name',)
    inlines = [ProductInline]

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    list_editable = ('price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    autocomplete_fields = ('category',)
    actions = [export_as_csv]
    list_filter = (PriceRangeFilter, 'category',  'stock')

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')
    autocomplete_fields = ('user',)

class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
    autocomplete_fields = ('user', 'product')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    autocomplete_fields = ('user', 'product')
    
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__name')
    autocomplete_fields = ('order', 'product')
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'get_total')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]
    actions = [export_as_csv]
    
    @admin.display(description='Total (Ar)')
    def get_total(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('items')
    

#model registration with the personnalized admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(CustomerProfile, CustomerProfileAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(WishlistItem, WishlistItemAdmin)
admin_site.add_action(export_as_csv)