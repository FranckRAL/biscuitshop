from django.urls import path
from django.conf.urls.static import static
from . import views
from django.conf import settings

urlpatterns = [
    
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('products/', views.products_list_view, name='product-list'),
    path('product/<int:product_id>/detail/', views.product_detail_view, name='product-detail'),
    
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/substract/<int:product_id>/', views.substract_item_qty_from_cart, name='substract-from-cart'),
    
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    
    
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment/<int:order_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('mvola/callback/', views.mvola_callback, name='mvola_callback')
    
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)