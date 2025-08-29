from django.db import models
from ecom.models import BaseModel
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(BaseModel):
    cat_name = models.CharField(max_length=100)
    cat_img = models.ImageField(upload_to='category_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.cat_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.cat_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class Product(BaseModel):
    pro_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.IntegerField()
    product_desc = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.pro_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.pro_name

    def get_product_price(self, size=None, color=None):
        """Return base + size + color variant price if provided."""
        final_price = self.price

        if size:
            size_variant = self.size_variant.filter(size_name=size).first()
            if size_variant:
                final_price += size_variant.price

        if color:
            color_variant = self.color_variant.filter(color_name=color).first()
            if color_variant:
                final_price += color_variant.price

        return final_price

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.reviews.count()


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product.pro_name}"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"
class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=50, unique=True)
    is_expired= models.BooleanField(default=False)
    discount_price= models.IntegerField(default=100)
    minimun_amount= models.IntegerField(default=1000)