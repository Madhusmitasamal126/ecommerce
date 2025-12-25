from django.urls import path
from account import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('activate/<str:token>/', views.activate_account, name='activate'),
    # path('', views.index, name='index'), 
    # Product
    
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),


    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("cart/add/<uuid:product_id>/", views.add_to_cart, name='add_to_cart'),
    path("cart/buy/<uuid:product_id>/", views.buy_now, name='buy_now'),
    path('cash-on-delivery/', views.cash_on_delivery, name='cash_on_delivery'),
    path('order/confirm/', views.order_confirm, name='order_confirm'),

    # Coupon
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("clear-coupon/", views.clear_coupon, name="clear_coupon"),

    # Checkout flow
    path('checkout/', views.checkout, name='checkout'),   # Cart summary only
    path("address/", views.address_page, name="address_page"),     # Address step
    path("payment/", views.payment, name="payment"),      # Payment step
    path("payment-success/", views.payment_success, name="payment_success"),

    # Orders
   path("account/order/confirm/", views.order_confirm, name="order_confirm"),
    path("account/order/track/<int:order_id>/", views.track_order, name="track_order"),



      # Forgot Password
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

   path('password-reset-confirm/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(
         template_name='accounts/password_reset_confirm.html'
     ), name='password_reset_confirm'),


    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

]