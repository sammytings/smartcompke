from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Brand
from app.services.brand_logo import BrandLogoService


@receiver(post_save, sender=Brand)
def fetch_brand_logo(sender, instance, created, **kwargs):

    print("Signal reached")

    if created and not instance.logo:
        print("Calling BrandLogoService...")
        BrandLogoService.fetch(instance)
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Category
from .services.category_icon_service import CategoryIconService


@receiver(post_save, sender=Category)
def category_icon(sender, instance, created, **kwargs):

    if created and not instance.icon:
        CategoryIconService.assign_icon(instance)

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Customer


@receiver(user_logged_in)
def save_customer(sender, request, user, **kwargs):

    Customer.objects.update_or_create(

        user=user,

        defaults={

            "email": user.email,

            "active": user.is_active,

        }

    )
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import StaffProfile


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):

    if created:

        StaffProfile.objects.create(
            user=instance
        )


@receiver(post_save, sender=User)
def save_staff_profile(sender, instance, **kwargs):

    instance.staff_profile.save()