
class Cart:
    """A shopping cart class to manage cart operations within a user's session.
    """
    def __init__(self, request):
        """init a cart object in the session

        Args:
            request (Request): request
        """
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
    
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
            self.save()
    
    def save(self):
        """save the change and reload the session
        """
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