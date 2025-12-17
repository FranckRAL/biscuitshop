from .cart import Cart

def cart(request):
    cart_instance = Cart(request)
    return {
        'cart': cart_instance,
        'cart_count': len(cart_instance),
        'cart_total_price': cart_instance.get_total_price()
    }