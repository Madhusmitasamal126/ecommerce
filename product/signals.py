from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import SizeVariant, ColorVariant


@receiver(post_migrate)
def create_defaults(sender, **kwargs):
    if sender.name == "product":
        # Default Sizes
        for s in ["S", "M", "L", "XL", "XXL"]:
            SizeVariant.objects.get_or_create(size_name=s)

        # Default Colors
        for c in ["Red", "Blue", "Green", "Black", "White", "Yellow"]:
            ColorVariant.objects.get_or_create(color_name=c)
