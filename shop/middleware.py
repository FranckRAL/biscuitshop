from .cart.cart import Cart
from .wishlist.wishlist import Wishlist

class CartMiddleware:
    """Automatically create a cart for all users (anonymous + authenticated)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Initialize cart for every request if not exists
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        # Attach Cart instance to request for easy access
        request.cart = Cart(request)
        
        response = self.get_response(request)
        return response
    
class WishlistMiddleware:
    """Automatically create a wishlist for all users (anonymous + authenticated)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Initialize wishlist for ALL users (not just authenticated)
        if 'wishlist' not in request.session:
            request.session['wishlist'] = []
            
        # Attach Wishlist instance to request for easy access
        request.wishlist = Wishlist(request)
        
        response = self.get_response(request)
        return response