from shop.models import Product, CartItem

class Cart:
    """A shopping cart class to manage cart operations within a user's session.
    """
    def __init__(self, request):
        """init a cart object in the session

        Args:
            request (Request): request
        """
        self.session = request.session
        self.is_authenticated: bool = request.user.is_authenticated
        self.request = request
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
        self._sync_cart_session_and_db()
    
    def add_item(self, product, quantity=1):
        """Add a product to the cart or update its quantity.

        Args:
            product (Product): Product to add
            quantity (int, optional): Quantity of the product to add. Defaults to 1.
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                "product_id": product_id,
                "quantity": 0,
                "price": str(product.price)
            }
            
        if self.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=self.request.user,
                    product=product,
                    quantity=quantity,
                    session_key=self.request.session.session_key
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                    
            except Product.DoesNotExist:
                print('Product not found')
            except Exception as e:
                print('Error adding to cart:', e)
            
        self.cart[product_id]["quantity"] += quantity
        self.save()
    
    def substract_number_of_item(self, product_or_id, quantity=1):
        """Substract quantity of a product in the cart.
        Args:
            product_or_id (Product or int/str): Product object or product ID
            quantity (int, optional): Quantity of the product to subtract. Defaults to 1.
        """
        # Handle both Product object and product_id
        if hasattr(product_or_id, 'id'):
            product_id = str(product_or_id.id)
        else:
            product_id = str(product_or_id)
            
        if product_id in self.cart:
            self.cart[product_id]["quantity"] -= quantity
            if self.cart[product_id]["quantity"] <= 0:
                del self.cart[product_id]
                
        if self.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                cart_item = CartItem.objects.get(user=self.request.user, product=product)
                cart_item.quantity -= quantity
                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()
                    
            except Product.DoesNotExist:
                pass
            except CartItem.DoesNotExist:
                pass

        self.save()
    
    def remove_item(self, product_or_id):
        """Remove a product from the cart.

        Args:
            product_or_id (Product or int/str): Product object or product ID
        """
        # Handle both Product object and product_id
        if hasattr(product_or_id, 'id'):
            product_id = str(product_or_id.id)
        else:
            product_id = str(product_or_id)
            
        if product_id in self.cart:
            del self.cart[product_id]
            
        if self.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                cart_item = CartItem.objects.get(user=self.request.user, product=product)
                cart_item.delete()
            except Product.DoesNotExist:
                pass
            except CartItem.DoesNotExist:
                pass

        self.save()
    
    def save(self):
        """save the change and reload the session
        """
        self._sync_cart_session_and_db()
        self.session.modified = True
    
    def __len__(self):
        """Return the total number of items in the cart.

        Returns:
            int: total number of items
        """
        return sum(item["quantity"] for item in self.cart.values())
    
    def __iter__(self):
        """Allow iteration over cart items"""
        return iter(self.cart.values())
    
    def get_total_price(self):
        """Return the total price of items in the cart.

        Returns:
            float: total price
        """
        return sum(float(item["price"]) * item["quantity"] for item in self.cart.values())
    
    def _sync_cart_session_and_db(self):
        if not self.is_authenticated:
            return

        db_cart = CartItem.objects.filter(user=self.request.user)
        db_cart_products = set(db_cart.values_list('product_id', flat=True))

        session_cart_products = set(int(pid) for pid in self.cart.keys())

        # Compute differences
        item_to_delete = db_cart_products - session_cart_products
        item_to_add = session_cart_products - db_cart_products
        item_to_update = session_cart_products.intersection(db_cart_products)

        # Delete items not in session
        if item_to_delete:
            CartItem.objects.filter(user=self.request.user, product_id__in=item_to_delete).delete()

        # Add new items from session
        for product_id in item_to_add:
            product = Product.objects.get(id=product_id)
            CartItem.objects.create(
                user=self.request.user,
                product=product,
                quantity=self.cart[str(product_id)]["quantity"],
                price=self.cart[str(product_id)]["price"],  # assuming you added a price field
            )

        # Update existing items if quantity/price differ
        for product_id in item_to_update:
            session_item = self.cart[str(product_id)]
            try:
                db_item = CartItem.objects.get(user=self.request.user, product_id=product_id)
                updated = False

                # check quantity
                if db_item.quantity != session_item["quantity"]:
                    db_item.quantity = session_item["quantity"]
                    updated = True

                # check price
                if hasattr(db_item, "price") and db_item.product.price != session_item["price"]:
                    db_item.product.price = session_item["price"]
                    updated = True

                if updated:
                    db_item.save()

            except CartItem.DoesNotExist:
                pass

        self.session.modified = True
