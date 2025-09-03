from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_page, name='categories_page'),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path('checkout/', views.checkout, name='checkout'),
    path("address/", views.address, name="address"),   # 👈 add this
    # path("confirmation/", views.order_confirmation, name="order_confirmation"),
    path("add-review/<uuid:product_id>/", views.add_review, name="add_review"),
    path('search/', views.search_results, name='search_results'),
    path("<slug:slug>/", views.get_product, name="get_product"),   # keep LAST
]



