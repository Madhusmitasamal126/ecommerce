from django.db import models
from django.contrib.auth.models import User
from ecom.models import BaseModel
from product.models import Product, Coupon
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from ecom.emails import send_account_activation_email
from django.utils import timezone


# ---------------- PROFILE ----------------
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_img = models.ImageField(upload_to='profile_images', null=True, blank=True)

    def __str__(self):
        return self.user.username

# ---------------- CART ----------------
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey('product.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_subtotal(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def get_discount(self):
        if self.coupon:
            return (self.get_subtotal() * self.coupon.discount) / 100
        return 0

    def get_total(self):
        return self.get_subtotal() - self.get_discount()

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_size = models.CharField(max_length=50, null=True, blank=True)
    selected_color = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # ✅ Use default instead of auto_now_add

    def total_price(self):
        return self.product.get_product_price(
            size=self.selected_size, color=self.selected_color
        ) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.pro_name}"

# ---------------- COUPON ----------------
class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.FloatField(default=0)
    minimum_amount = models.FloatField(default=0)

    def __str__(self):
        return self.code

# ---------------- ADDRESS ----------------
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}"

# ---------------- PAYMENT ----------------
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"

# ---------------- SIGNALS ----------------
@receiver(post_save, sender=User)
def create_profile_and_cart(sender, instance, created, **kwargs):
    if created:
        token = str(uuid.uuid4())
        Profile.objects.create(user=instance, email_token=token)
        Cart.objects.create(user=instance)
        if instance.email:
            send_account_activation_email(instance.email, token)

class Order(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders'   # <-- add this
    )
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=(
            ("Processing", "Processing"),
            ("Shipped", "Shipped"),
            ("Out for Delivery", "Out for Delivery"),
            ("Delivered", "Delivered"),
        ),
        default="Processing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.CharField(max_length=50, default="3-5 business days")

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
