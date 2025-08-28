from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from account.models import Profile, Cart, CartItem
from product.models import Coupon
from django.views.decorators.http import require_POST
from product.models import Product

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

    # Clear existing cart for buy now
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

    return redirect("checkout")   # you can build checkout page later



def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = authenticate(username=username, password=password)
        if user_obj:
            if not user_obj.profile.is_email_verified:
                messages.error(request, "Email is not verified. Please check your inbox.")
                return HttpResponseRedirect(request.path_info)
            login(request, user_obj)
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password.")
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return HttpResponseRedirect(request.path_info)

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created successfully! Please check your email to verify your account.")
        return redirect("login")

    return render(request, 'accounts/register.html')


def activate_account(request, token):
    try:
        profile = Profile.objects.get(email_token=token)
        profile.is_email_verified = True
        profile.save()
        messages.success(request, "Your account has been activated successfully!")
        return redirect("login")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired activation link.")
        return redirect("register")


@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(coupon_code__iexact=coupon_code)

            except Coupon.DoesNotExist:
                messages.warning(request, 'Invalid Coupon')
                return redirect("cart")
            if cart_obj.coupon:
                messages.warning(request, 'Coupon already applied')
                return redirect("cart")

            minimum_amount = getattr(coupon_obj, 'minimum_amount', 0)
            if cart_obj.get_subtotal() < float(minimum_amount):
    # your existing code for handling minimum amount

                messages.warning(request, f'Cart total must be at least ₹{coupon_obj.minimum_amount} to apply this coupon')
                return redirect("cart")

            cart_obj.coupon = coupon_obj
            cart_obj.save()
            messages.success(request, f'Coupon "{coupon_obj.name}" applied successfully!')

    context = {
        'cart': cart_obj,
        'items': cart_obj.items.all(),
        'subtotal': cart_obj.get_subtotal(),
        'discount': cart_obj.get_discount(),
        'total': cart_obj.get_total(),
    }
    return render(request, 'product/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    except CartItem.DoesNotExist:
        messages.warning(request, "Item not found in your cart.")
    return redirect("cart")


@login_required
def clear_coupon(request):
    cart = get_object_or_404(Cart, user=request.user)
    if cart.coupon:
        cart.coupon = None
        cart.save()
        messages.success(request, "Coupon removed successfully.")
    else:
        messages.warning(request, "No coupon applied.")
    return redirect("cart")
