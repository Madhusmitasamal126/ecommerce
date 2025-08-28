from django.urls import path
from account import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('activate/<str:token>/', views.activate_account, name='activate'),

    path('cart/', views.cart, name='cart'),
    path("cart/remove/<uuid:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear-coupon/", views.clear_coupon, name="clear_coupon"),

    # ✅ Add to cart & buy now
    path("cart/add/<uuid:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/buy/<uuid:product_id>/", views.buy_now, name="buy_now"),
]

