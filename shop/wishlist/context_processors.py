from .wishlist import Wishlist

def wishlist(request):
    """Context processor to add wishlist to context"""
    # Get or create wishlist from middleware
    if not hasattr(request, 'wishlist'):
        request.wishlist = Wishlist(request)
    
    return {
        'wishlist': [int(pid) for pid in request.wishlist.get_products()],      # List of product IDs
        'wishlist_count': request.wishlist.__len__(),   # Count of items
    }