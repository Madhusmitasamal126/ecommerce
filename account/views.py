from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from .models import Order


from account.models import Profile, Cart, CartItem, Address, Coupon, Payment
from product.models import Product
from account.forms import AddressForm

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ---------------- PRODUCT DETAIL ----------------
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "product/product_detail.html", {"product": product})

# ---------------- CART / BUY NOW ----------------
@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size")
    color = request.POST.get("color")
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        selected_size=size if size else None,
        selected_color=color if color else None,
    )
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    messages.success(request, f"{product.pro_name} added to cart.")
    return redirect("cart")

@login_required
@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size")
    color = request.POST.get("color")
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity,
        selected_size=size if size else None,
        selected_color=color if color else None,
    )
    return redirect("checkout")

# ---------------- LOGIN / REGISTER ----------------
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # go to originally requested page
            return redirect('/')  # default redirect
        else:
            messages.error(request, "Invalid credentials.")
            return redirect(request.path_info)
    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path_info)
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username exists.")
            return redirect(request.path_info)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email exists.")
            return redirect(request.path_info)
        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created! Check email for verification.")
        return redirect("login")
    return render(request, 'accounts/register.html')

def activate_account(request, token):
    try:
        profile = Profile.objects.get(email_token=token)
        profile.is_email_verified = True
        profile.save()
        messages.success(request, "Account activated successfully!")
        return redirect("login")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired link.")
        return redirect("register")

# ---------------- CART ----------------
@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    context = {
        "cart": cart_obj,
        "items": cart_obj.items.all(),
        "subtotal": cart_obj.get_subtotal(),
        "discount": cart_obj.get_discount(),
        "total": cart_obj.get_total(),
    }
    return render(request, "product/cart.html", context)

@login_required
def remove_from_cart(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        messages.success(request, "Item removed from cart")
    except CartItem.DoesNotExist:
        messages.warning(request, "Item not found")
    return redirect("cart")

# ---------------- CHECKOUT ----------------
# @login_required
# def checkout(request):
#     cart = get_object_or_404(Cart, user=request.user)
#     cart_items = cart.items.all()
#     total_price = sum(item.product.pro_price * item.quantity for item in cart_items)

#     selected_address_id = request.session.get("selected_address")
#     selected_address = None
#     if selected_address_id:
#         selected_address = Address.objects.filter(id=selected_address_id, user=request.user).first()

#     return render(request, "product/checkout.html", {
#         "checkout_cart": cart_items,
#         "total_price": total_price,
#         "address": selected_address
#     })

# ---------------- PAYMENT ----------------
@login_required
def payment(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect("cart")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Ensure amount is at least 1 INR
    if total_price < 1:
        messages.error(request, "Order total must be at least ₹1 to proceed with online payment.")
        return redirect("checkout")

    address = Address.objects.filter(user=request.user).first()
    razorpay_order = client.order.create({
        "amount": int(total_price * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "address": address,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "payment": razorpay_order
    }
    return render(request, "product/payment.html", context)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            Payment.objects.filter(razorpay_order_id=order_id).update(
                razorpay_payment_id=payment_id, 
                razorpay_signature=signature,
                status="success"
            )
            return redirect("order_confirmation")
        except:
            Payment.objects.filter(razorpay_order_id=order_id).update(status="failed")
            messages.error(request, "Payment verification failed.")
            return redirect("payment")

# ---------------- CASH ON DELIVERY ----------------
@login_required
@require_POST
def cash_on_delivery(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect("cart")
    # Optionally create a Payment record with COD
    # Payment.objects.create(user=request.user, amount=cart.get_total(), payment_method="COD", status="success")
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    messages.success(request, "Your order has been placed successfully with Cash on Delivery!")
    return redirect("order_confirmation")

# ---------------- ORDER CONFIRMATION ----------------

# ---------------- ORDER TRACKING ----------------
@login_required
def order_tracking(request):
    payments = Payment.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "product/order.html", {"payments": payments})

# ---------------- COUPON ----------------
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code")
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
            request.session["coupon_id"] = coupon.id
            messages.success(request, f"Coupon {coupon.code} applied successfully!")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid or expired coupon.")
    return redirect("checkout")

def clear_coupon(request):
    if "coupon_id" in request.session:
        del request.session["coupon_id"]
        messages.info(request, "Coupon removed.")
    return redirect("checkout")


def cash_on_delivery(request):
    if request.method == 'POST':
        # You can process the order here, e.g., mark as COD
        messages.success(request, "Order placed successfully with Cash on Delivery!")
        return redirect('order_confirm')  # Make sure you have a URL named 'order_confirm'
    else:
        return redirect('payment')  # redirect back if someone tries GET
    
@login_required
def order_confirm(request):
    order = Order.objects.filter(user=request.user).last()
    return render(request, "product/order_confirmation.html", {"order": order})

# @login_required
# def order_confirm(request, order_id=None):
#     if order_id:
#         order = get_object_or_404(Order, id=order_id, user=request.user)
#     else:
#         order = Order.objects.filter(user=request.user).order_by("-created_at").first()

#     if not order:
#         messages.warning(request, "No order found.")
#         return redirect("orders")

#     return render(request, "product/order_confirmation.html", {"order": order})



@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'track_order.html', {'order': order})


# address_page view
@login_required
def address_page(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    form = AddressForm()

    if request.method == "POST":
        # Case 1: User selects an existing address
        if 'selected_address' in request.POST:
            address_id = request.POST.get('selected_address')
            request.session['selected_address_id'] = address_id
            return redirect('checkout')  # redirect to checkout after selection

        # Case 2: User adds a new address
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()
            request.session['selected_address_id'] = new_address.id
            return redirect('checkout')

    context = {
        'addresses': addresses,
        'form': form
    }
    return render(request, 'product/address.html', context)




@login_required
def checkout(request):
    user = request.user
    checkout_cart = CartItem.objects.filter(cart__user=user)
    total_price = sum(item.product.price * item.quantity for item in checkout_cart)

    selected_address = None
    address_id = request.session.get('selected_address_id')
    if address_id:
        try:
            selected_address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            selected_address = None

    context = {
        'checkout_cart': checkout_cart,
        'total_price': total_price,
        'address': selected_address
    }
    return render(request, 'product/checkout.html', context)


# def track_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     return render(request, 'track_order.html', {'order': order})
