import logging

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_order_confirmation_email(request, order):
    """
    Sends a professional HTML order confirmation email.

    Any email errors are logged but do not interrupt checkout.
    """

    try:
        items = (
            order.items
            .select_related(
                "product",
                "variant",
            )
        )

        context = {
            "order": order,
            "items": items,
            "site_name": "SmartComputersKE",
            "tracking_url": request.build_absolute_uri(
                f"/orders/{order.order_id}/receipt/"
            ),
        }

        html_message = render_to_string(
            "emails/order_confirmation.html",
            context,
        )

        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=f"Order Confirmation - {order.order_id}",
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )

        email.attach_alternative(
            html_message,
            "text/html",
        )

        # THIS ACTUALLY SENDS THE EMAIL
        sent = email.send(fail_silently=False)

        print("=" * 60)
        print("EMAIL SENT RESULT:", sent)
        print("TO:", order.email)
        print("FROM:", settings.DEFAULT_FROM_EMAIL)
        print("=" * 60)

        logger.info(
            "Order confirmation sent to %s",
            order.email,
        )

        return True

    except Exception as e:

        print("=" * 60)
        print("EMAIL ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 60)

        logger.exception(
            "Unable to send order confirmation for %s",
            order.order_id,
        )

        return False
import random


def generate_otp():
    return str(random.randint(100000, 999999))

from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(user, otp):

    subject = "Verify Your SmartComputersKe Account"

    message = f"""
Hello {user.first_name},

Welcome to SmartComputersKe Technologies.

Your verification code is:

{otp}

This code expires in 10 minutes.

If you didn't create this account, simply ignore this email.

SmartComputersKe Technologies
Kimathi Street, Nairobi CBD
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
from .models import Cart

def get_cart(request):

    print("=" * 60)
    print("GET CART")
    print("Authenticated:", request.user.is_authenticated)
    print("User:", request.user)

    if not request.session.session_key:
        request.session.create()

    print("Session:", request.session.session_key)

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={"user": None},
        )

    print("Cart:", cart.id)
    print("Created:", created)
    print("Items:", cart.items.count())
    print("=" * 60)

    return cart
from .models import Wishlist
from .models import Wishlist


def get_wishlist(request):
    """
    Returns the current user's wishlist.
    Supports authenticated and anonymous users.
    """

    if request.user.is_authenticated:

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user
        )

    else:

        if not request.session.session_key:
            request.session.create()

        wishlist, created = Wishlist.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={
                "user": None,
            },
        )

    return wishlist