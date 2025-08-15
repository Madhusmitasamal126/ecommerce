from django.db import models
from django.contrib.auth.models import User
from ecom.models import BaseModel

class Profile(BaseModel):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email=models.BooleanField(default=False)
    email_tokan=models.CharField(max_length=100, null=True, blank=True)
    profile_img=models.ImageField(upload_to='profile_images')
# Create your models here.
