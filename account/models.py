from django.db import models
from django.contrib.auth.models import User
from ecom.models import BaseModel
from product.models import Product, Coupon
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from ecom.emails import send_account_activation_email


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_img = models.ImageField(upload_to='profile_images', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_subtotal(self):
        return sum([item.total_price() for item in self.items.all()])

    def get_discount(self):
        if self.coupon:
            return float(self.coupon.discount_price)
        return 0
    def get_total(self):
        return max(self.get_subtotal() - self.get_discount(), 0)



class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_size = models.CharField(max_length=50, null=True, blank=True)
    selected_color = models.CharField(max_length=50, null=True, blank=True)

    def total_price(self):
        return self.product.get_product_price(
            size=self.selected_size, color=self.selected_color
        ) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.pro_name}"

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.FloatField(default=0)   # default added
    minimum_amount = models.FloatField(default=0) # <-- add this if missing
    # optional: add expiry, active, etc.


    def __str__(self):
        return self.code


# --- Auto create Profile and Cart ---
@receiver(post_save, sender=User)
def create_profile_and_cart(sender, instance, created, **kwargs):
    if created:
        token = str(uuid.uuid4())
        Profile.objects.create(user=instance, email_token=token)
        Cart.objects.create(user=instance)
        if instance.email:
            send_account_activation_email(instance.email, token)
