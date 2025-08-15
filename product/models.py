from django.db import models
from ecom.models import BaseModel


class Category(BaseModel):
    cat_name = models.CharField(max_length=100)
    cat_img = models.ImageField(upload_to='category_images/')
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.cat_name

class Product(BaseModel):
    pro_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.IntegerField()
    product_desc = models.TextField()

    def __str__(self):
        return self.pro_name



class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product.pro_name}"
# Create your models here.
