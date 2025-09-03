"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from product import views as product_views
# from cart import views as cart_views

urlpatterns = [
    path('', include('home.urls')),               # Home app
    path('product/', include('product.urls')),    # Product app
    path('account/', include('account.urls')),    # Account app
    path('admin-panel/', admin.site.urls),        # Admin
    path('category/<slug:slug>/', product_views.category_detail, name='category_detail_root'),
    # path('checkout/', cart_views.checkout, name='checkout'),
    path('cart/', include('cart.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
