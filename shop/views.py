from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, Category, CustomerProfile, Order, OrderItem
from .forms import CustomerRegistrationForm, CheckoutForm
from django.contrib.auth.forms import AuthenticationForm
from shop.payment.mvola_service import MvolaPaymentService
from shop.payment.paypal_service import PaypalPaymentService
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
import logging
import json

logger = logging.getLogger(__name__)


def home(request):
    biscuits = Product.objects.all()
    context = {
        'biscuits': biscuits,
    }
    return render(request, 'shop/home.html', context)

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect to next page or home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'page': 'login'
    }
    return render(request, 'shop/login_register.html', context)

def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            
            # Get or create CustomerProfile (signal should handle this, but ensure it exists)
            customer_profile, created = CustomerProfile.objects.get_or_create(user=user)
            
            # Update profile with additional data if provided
            if form.cleaned_data.get('phone_number'):
                customer_profile.phone_number = form.cleaned_data['phone_number']
            if form.cleaned_data.get('address'):
                customer_profile.address = form.cleaned_data['address']
            customer_profile.save()
            
            # Auto-login the user
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            
            return redirect('home')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomerRegistrationForm()
    
    context = {
        'form': form,
        'page': 'register'
    }
    return render(request, 'shop/login_register.html', context)

def logout_view(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.success(request, f'Logged out successfully. See you soon!')
    return redirect('home')

def products_list_view(request):
    """Display products with category filtering"""
    products = Product.objects.all()
    categories = Category.objects.all()
    current_category = 0
    
    if request.method == 'GET':
        category_id = request.GET.get('category')
        if category_id and category_id != '0':
            products = products.filter(category__id=category_id)
            current_category = int(category_id)
    products_page = Paginator(products, 8)  # Show 10 products per page
    page_number = request.GET.get('page')
    context = {
        'products': products_page.get_page(page_number),
        'categories': categories,
        'current_category': current_category
    }
    return render(request, 'shop/products.html', context)

def product_detail_view(request, product_id):
    """Return product detail as JSON (for modal display)"""
    try:
        product = Product.objects.get(id=product_id)
        # Get wishlist from session
        wishlist = request.session.get('wishlist', [])
        context = {
            'product': product,
            'wishlist': wishlist
        }
        html = render_to_string('shop/product_detail.html', context, request=request)
        return JsonResponse({'success': True, 'html': html})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

# Cart management views
def cart_view(request):
    """Display shopping cart"""
    cart = request.cart
    
    # Get product IDs from cart
    product_ids = [int(pid) for pid in cart.cart.keys()]
    
    # Fetch products
    if product_ids:
        products_in_cart = Product.objects.filter(id__in=product_ids)
        products_dict = {str(p.id): p for p in products_in_cart}    #type: ignore
    else:
        products_dict = {}
    
    # Build cart display
    cart_items = []
    for product_id_str, item_data in cart.cart.items():
        product = products_dict.get(product_id_str)
        if product:
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'subtotal': float(item_data['price']) * item_data['quantity']
            })
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart.get_total_price(),
    }
    return render(request, 'shop/cart.html', context)

@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Add product to cart (AJAX)"""
    try:
        product = Product.objects.get(id=product_id)
        cart = request.cart
        cart.add_item(product)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.__len__(),
                'cart_total_price': float(cart.get_total_price())
            })
            
        return redirect('cart')
    
    except Product.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
        return redirect('product-list')

    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return redirect('product-list')


def remove_from_cart(request, product_id):
    """Remove product from cart"""
    try:
        cart = request.cart
        cart.remove_item(product_id)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Product removed from cart.',
                'cart_count': cart.__len__(),
                'cart_total_price': float(cart.get_total_price())
            })
            
    except Exception as e:
        pass
    return redirect('cart')


def substract_item_qty_from_cart(request, product_id):
    """Decrease product quantity in cart"""
    try:
        cart = request.cart
        cart.substract_number_of_item(product_id)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Product quantity decreased.',
                'cart_count': cart.__len__(),
                'cart_total_price': float(cart.get_total_price())
            })
            
    except Exception as e:
        pass
    return redirect('cart')

#wishlist management views 
def wishlist_view(request):
    """Display wishlist"""
    wishlist = request.wishlist
    
    # Get product IDs from wishlist
    product_ids = wishlist.get_products()
    
    # Fetch actual Product objects
    if product_ids:
        wishlist_products = Product.objects.filter(id__in=product_ids)
    else:
        wishlist_products = Product.objects.none()
    
    context = {
        'wishlist_products': wishlist_products,
    }
    return render(request, 'shop/wishlist.html', context)


@require_http_methods(["POST"])
def toggle_favorite(request, product_id):
    """Toggle product in wishlist (add/remove via AJAX)"""
    try:
        product = Product.objects.get(id=product_id)
        wishlist = request.wishlist  
        
        # Check if product is already in wishlist
        is_favorited = wishlist.is_in_wishlist(product_id)
        # Toggle
        if is_favorited:
            wishlist.remove(product_id)
            was_added = False
            message = f'{product.name} removed from wishlist.'
        else:
            wishlist.add(product_id)
            was_added = True
            message = f'{product.name} added to wishlist.'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_favorited': was_added,      
                'wishlist_count': wishlist.__len__(),
                'message': message
            })
        
        return redirect(request.META.get('HTTP_REFERER', 'product-list'))
        
    except Product.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
        return redirect('product-list')
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return redirect('product-list')


#Payment logic views
@login_required(login_url='login')
def checkout_view(request):
    """Handle checkout and order creation"""
    cart = request.cart
    
    # Redirect if cart is empty
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Extract customer phone based on payment method
            payment_method = form.cleaned_data["payment_method"]
            customer_phone = ""
            
            # Get phone number based on payment method
            if payment_method in ["mvola", "orange", "airtel"]:
                customer_phone = form.cleaned_data.get("wallet_number", "")
            elif payment_method == "card":
                # For card, we don't need phone
                customer_phone = ""
            elif payment_method == "paypal":
                # For PayPal, we don't need phone
                customer_phone = ""
            
            # Validate phone number is present for mobile money
            if payment_method in ["mvola", "orange", "airtel"] and not customer_phone:
                messages.error(request, f"Wallet number is required for {payment_method.title()} payment.")
                return render(request, 'shop/checkout_success.html', {
                    'form': form,
                    'cart_items': cart.get_items(),
                    'cart_total_price': cart.get_total_price(),
                    'cart_items_count': len(cart)
                })
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                status='pending',
                total_price=Decimal('0.00'),
                payment_method=payment_method,
                customer_phone=customer_phone,
                customer_address=""
            )
            
            # Add items to order
            total = Decimal('0.00')
            for item in cart:
                product = Product.objects.get(id=item["product_id"])
                quantity = item["quantity"]
                price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                total += price * quantity
            
            order.total_price = total
            order.save()
            
            logger.info(f"Order {order.id} created with payment method {payment_method} and phone {customer_phone}") #type: ignore
            
            if payment_method == "cod":
                # Cash on Delivery - mark as completed and clear cart
                order.status = 'completed'
                order.save()
                cart.clear()
                messages.success(request, 'Order placed successfully! We will contact you soon.')
                return redirect('order_success', order_id=order.id) #type: ignore
            else:
                # Online payment - redirect to payment processing
                cart.clear()
                return redirect('process_payment', order_id=order.id) #type: ignore
    else:
        form = CheckoutForm()
    
    # GET request - show checkout form with order summary
    context = {
        'cart_items': cart.get_items(),
        'cart_total_price': cart.get_total_price(),
        'cart_items_count': len(cart)
    }
    return render(request, 'shop/checkout_success.html', context)

#related to mvola payment
@login_required(login_url='login')
def process_payment(request, order_id):
    """Handle payment processing for different methods"""
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')

    if order.status != 'pending':
        return redirect('order_success', order_id=order.id) #type: ignore
    

    services = {
        "mvola": MvolaPaymentService(),
        "paypal": PaypalPaymentService(),
    }
    
    service = services.get(order.payment_method)
    if not service:
        messages.error(request, f'Payment method {order.payment_method} not supported.')
        return redirect('cart')
    
    try:
        result = service.initiate_payment(request, order)
        
        # For callback-based payments, just show pending page
        if result.get("notificationMethod") == "callback":
            logger.info(f"[Payment] Payment initiated for order {order.id}") #type: ignore
            messages.info(request, 'Payment is being processed. Please wait for confirmation...')
            return redirect('order_waiting', order_id=order.id) #type: ignore
        
        # For redirect-based payments
        if 'redirect_url' in result:
            return redirect(result["redirect_url"])
        
        return redirect('order_waiting', order_id=order.id) #type: ignore
        
    except Exception as e:
        logger.error(f"[Payment] Error initiating {order.payment_method}: {str(e)}")
        messages.error(request, 'Payment initiation failed. Please try again.')
        return redirect('checkout')

@require_http_methods(["GET"])
def order_waiting(request, order_id):
    """Show payment pending page with status updates"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        context = {'order': order}
        return render(request, 'shop/payment/order_waiting.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')

@login_required(login_url='login')
def order_success(request, order_id):
    """Display order success page"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Only show success if payment is completed
        if order.status != 'completed':
            return redirect('order_waiting', order_id=order.id) #type: ignore
        
        context = {'order': order}
        return render(request, 'shop/payment/order_success.html', context)
    
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')

@login_required(login_url='login')
@require_http_methods(["GET"])
def check_payment_status(request, order_id):
    """AJAX endpoint to check payment status (polling)"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Check if already completed
        if order.status == 'completed':
            return JsonResponse({
                "status": "completed",
                "redirect_url": reverse('order_success', args=[order.id]) #type: ignore
            })
        
        if order.status == 'failed':
            return JsonResponse({
                "status": "failed",
                "message": "Payment failed. Please try again."
            })
        
        # Check status from payment service
        service = MvolaPaymentService()
        result = service.check_status(order)
        
        response = {
            "status": result.get("status"),
            "order_status": result.get("order_status"),
            "message": result.get("message", "")
        }
        
        # If completed, provide redirect URL
        if result.get("order_status") == "completed":
            response["redirect_url"] = reverse('order_success', args=[order.id]) #type: ignore
        
        return JsonResponse(response)
        
    except Order.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Order not found"
        }, status=404)
    except Exception as e:
        logger.error(f"[Payment Status Check] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def mvola_callback(request):
    """Handle Mvola payment callback webhook"""
    try:
        data = json.loads(request.body)
        logger.info(f"[Mvola Callback] Received callback: {data.get('requestingOrganisationTransactionReference')}")
        
        # Validate required fields
        required_fields = ['requestingOrganisationTransactionReference', 'transactionStatus']
        if not all(field in data for field in required_fields):
            logger.error(f"[Mvola Callback] Missing required fields")
            return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)
        
        # Process callback
        service = MvolaPaymentService()
        response = service.handle_callback(data)
        
        if response.get("status") == "success":
            logger.info(f"[Mvola Callback] Payment processed successfully for order {response.get('order_id')}")
        
        return JsonResponse(response)
        
    except json.JSONDecodeError:
        logger.error(f"[Mvola Callback] Invalid JSON received")
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"[Mvola Callback] Error processing callback: {str(e)}", exc_info=True)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
