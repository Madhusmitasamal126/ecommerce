from django.urls import path
from account.views import login_page, register_page, activate_account

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('activate/<str:token>/', activate_account, name='activate'),
]
