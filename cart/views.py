from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import CartItem, Address
from account.forms import AddressForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import Order  # Make sure Order model exists


@login_required
def orders_view(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': user_orders}
    return render(request, 'product/orders.html', context)

@login_required
def checkout(request):
    # Get user's cart items
    try:
        cart_items = request.user.cart.items.all()
    except:
        cart_items = []

    total_price = sum([item.total_price() for item in cart_items])

    if request.method == 'POST':
        # Save cart and checkout info in session
        request.session['checkout_done'] = True
        request.session['checkout_data'] = {
            'full_name': request.POST.get('full_name', ''),
            'phone': request.POST.get('phone', ''),
            'street_address': request.POST.get('street_address', ''),
            'city': request.POST.get('city', ''),
            'state': request.POST.get('state', ''),
            'postal_code': request.POST.get('postal_code', ''),
            'country': request.POST.get('country', ''),
        }
        return redirect('address')

    return render(request, 'product/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def address(request):
    # Ensure user came from checkout
    if not request.session.get('checkout_done'):
        return redirect('checkout')

    user_addresses = Address.objects.filter(user=request.user)
    checkout_cart = request.user.cart.items.all()
    total_price = request.user.cart.get_total()

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            # User confirmed an existing address
            request.session['selected_address_id'] = selected_address_id
        else:
            # User submitted a new address
            form = AddressForm(request.POST)
            if form.is_valid():
                new_address = form.save(commit=False)
                new_address.user = request.user
                # If this is first address, set default
                if not user_addresses.exists():
                    new_address.default = True
                new_address.save()
                request.session['selected_address_id'] = new_address.id

        request.session['address_done'] = True
        return redirect('order_confirmation')

    form = AddressForm()
    return render(request, 'product/address.html', {
        'addresses': user_addresses,
        'checkout_cart': checkout_cart,
        'total_price': total_price,
        'form': form
    })


@login_required
def order_confirmation(request):
    if not request.session.get('address_done'):
        return redirect('checkout')

    checkout_data = request.session.get('checkout_data', {})

    # Clear session
    request.session.pop('checkout_done', None)
    request.session.pop('address_done', None)
    request.session.pop('checkout_data', None)

    return render(request, 'product/order_confirmation.html', {'checkout_data': checkout_data})
@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed successfully.")
    return redirect('address')
