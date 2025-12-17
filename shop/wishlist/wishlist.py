class Wishlist:
    def __init__(self, request) -> None:
        self.session = request.session
        wishlist = self.session.get('wishlist')
        if not wishlist:
            wishlist = self.session['wishlist'] = []
        self.wishlist = wishlist
        
    def add(self, product_id):
        """Add product to wishlist"""
        product_id = str(product_id)  # Ensure string for consistency
        if product_id not in self.wishlist:
            self.wishlist.append(product_id)
            self.save()
            
    def remove(self, product_id):
        """Remove product from wishlist"""
        product_id = str(product_id)  # Ensure string for consistency
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.save()
    
    def is_in_wishlist(self, product_id):
        """Check if product is in wishlist"""
        return str(product_id) in self.wishlist
            
    def save(self):
        """Save wishlist to session"""
        self.session['wishlist'] = self.wishlist
        self.session.modified = True
        
    def clear(self):
        """Clear wishlist"""
        self.session['wishlist'] = []
        self.wishlist = []
        self.session.modified = True
    
    def get_products(self):
        """Get product IDs in wishlist"""
        return self.wishlist
    
    def get_count(self):
        """Get number of items in wishlist"""
        return len(self.wishlist)
    
    def __len__(self):
        """Get number of items in wishlist"""
        return len(self.wishlist)
    
    def __iter__(self):
        """Iterate over Product objects in wishlist"""
        from shop.models import Product
        products = Product.objects.filter(id__in=self.wishlist)
        for product in products:
            yield product