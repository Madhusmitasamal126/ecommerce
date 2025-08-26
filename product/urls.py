from django.urls import path
from . import views

urlpatterns = [
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("<slug:slug>/", views.get_product, name="get_product"),
    path("add-review/<uuid:product_id>/", views.add_review, name="add_review"),
]
