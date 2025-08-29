from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('address/', views.address, name='address'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    # path('address/set-default/<int:address_id>/', views.set_default_address, name='set_default_address')
    path('orders/', views.orders_view, name='orders'),
]
