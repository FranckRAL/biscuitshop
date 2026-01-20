from shop.models import Product, WishlistItem
import logging

logger = logging.getLogger(__name__)


class Wishlist:
    def __init__(self, request) -> None:
        self.session = request.session
        self.request = request
        self.is_authenticated = request.user.is_authenticated
        wishlist = self.session.get('wishlist')
        if not wishlist:
            wishlist = self.session['wishlist'] = []
        self.wishlist = wishlist
        self._sync_wishlist_session_and_db()
        
    def add(self, product_id):
        """Add product to wishlist"""
        product_id = str(product_id)  # Ensure string for consistency
        if self.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                _ , created = WishlistItem.objects.get_or_create(user=self.request.user, product=product)
                if not created:
                    return
            except Exception as e:
                logger.error('Error adding to wishlist in the database: %s', e)
            
        if product_id not in self.wishlist:
            self.wishlist.append(product_id)
            self.save()

    def remove(self, product_id):
        """Remove product from wishlist"""
        product_id = str(product_id)
        
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            if self.is_authenticated:
                try:
                    product = Product.objects.get(id=product_id)
                    WishlistItem.objects.filter(user=self.request.user, product=product).delete()
                except Exception as e:
                    logger.error('Error removing from wishlist frome the database: %s', e)
            
        self.save()
    
    def is_in_wishlist(self, product_id):
        """Check if product is in wishlist"""
        if self.is_authenticated:
            try:
                product = Product.objects.get(id=int(product_id))
                return WishlistItem.objects.filter(user=self.request.user, product=product).exists()
            except Exception as e:
                logger.error('Error checking wishlist in the database: %s', e)
                return False
        
        return str(product_id) in self.wishlist
            
    def save(self):
        """Save wishlist to session"""
        self.session['wishlist'] = self.wishlist
        self._sync_wishlist_session_and_db()
        self.session.modified = True
        
    def clear(self):
        """Clear wishlist"""
        self.session['wishlist'] = []
        self.wishlist = []
        self._sync_wishlist_session_and_db()
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

    def _sync_wishlist_session_and_db(self):
        """Sync wishlist between session and database"""
        if not self.is_authenticated:
            return 

        session_ids = set(self.wishlist)  

        try:
            db_items = WishlistItem.objects.filter(user=self.request.user)
            db_ids = set(item.product_id for item in db_items) #type: ignore
        except Exception as e:
            print('Error syncing wishlist:', e)
            return

        # Remove items from DB that are NOT in session
        items_to_remove = db_ids - session_ids
        if items_to_remove:
            try:
                WishlistItem.objects.filter(
                    user=self.request.user,
                    product_id__in=items_to_remove
                ).delete()
            except Exception as e:
                print('Error removing items from wishlist:', e)

        # Add items to DB that ARE in session
        items_to_add = session_ids - db_ids
        try:
            for product_id in items_to_add:
                WishlistItem.objects.get_or_create(
                    user=self.request.user,
                    product_id=product_id
                )
        except Exception as e:
            print('Error adding items to wishlist:', e)

        self.request.session.modified = True

            
        
                    