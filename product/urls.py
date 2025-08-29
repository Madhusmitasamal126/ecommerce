from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_page, name='categories_page'),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path('checkout/', views.checkout, name='checkout'),
    path("add-review/<uuid:product_id>/", views.add_review, name="add_review"),

    # 👈 put search BEFORE the catch-all slug
    path('search/', views.search_results, name='search_results'),

    # catch-all slug for product detail
    path("<slug:slug>/", views.get_product, name="get_product"),  
]


