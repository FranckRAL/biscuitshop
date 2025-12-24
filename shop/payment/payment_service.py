class PaymentService:
    def initiate_payment(self, request, order):
        """Initiate payment and return result dict with optional redirect_url"""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def check_status(self, order):
        """Check payment status and return status string ('completed', 'failed', 'pending')"""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def handle_callback(self, data):
        """Handle payment callback from payment provider"""
        raise NotImplementedError("Subclasses must implement this method.")