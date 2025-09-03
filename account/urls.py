from django.urls import path
from account import views

urlpatterns = [
    # Auth
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('activate/<str:token>/', views.activate_account, name='activate'),

    # Product
    
    path("product/<slug:slug>/", views.get_product, name="get_product"),


    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("cart/add/<uuid:product_id>/", views.add_to_cart, name='add_to_cart'),
    path("cart/buy/<uuid:product_id>/", views.buy_now, name='buy_now'),

    # Coupon
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("clear-coupon/", views.clear_coupon, name="clear_coupon"),

    # Checkout flow
    path('checkout/', views.checkout, name='checkout'),   # Cart summary only
    # path("address/", views.address_page, name="address_page"),     # Address step
    path("payment/", views.payment, name="payment"),      # Payment step
    path("payment-success/", views.payment_success, name="payment_success"),

    # Orders
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path("order/tracking/", views.order_tracking, name="order_tracking"),
]
