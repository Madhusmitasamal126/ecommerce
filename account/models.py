from django.db import models
from django.contrib.auth.models import User
from ecom.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from ecom.emails import send_account_activation_email


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_img = models.ImageField(upload_to='profile_images', null=True, blank=True)


@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    if created:
        # generate token FIRST
        email_token = str(uuid.uuid4())

        # create profile with token
        Profile.objects.create(user=instance, email_token=email_token)

        # send email
        if instance.email:
            send_account_activation_email(instance.email, email_token)
