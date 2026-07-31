from .models import Category

def categories(request):

    return {

        "categories":

        Category.objects.all()

    }
def compare_context(request):

    compare = request.session.get("compare", [])

    return {
        "compare_count": len(compare),
    }
from .models import Cart, Wishlist
from .models import Cart, Wishlist

from .utils import get_cart
from .models import Wishlist

from .models import Cart, Wishlist

from .utils import get_cart, get_wishlist


def global_ecommerce_data(request):
    """
    Global cart and wishlist context.
    Works for authenticated and anonymous users.
    """

    context = {
        "cart_items": [],
        "cart_count": 0,
        "cart_subtotal": 0,
        "wishlist_count": 0,
    }

    # -------------------------
    # CART
    # -------------------------
    try:
        cart = get_cart(request)

        context["cart_items"] = (
            cart.items.filter(
                saved_for_later=False
            ).select_related(
                "product",
                "variant",
                "product__brand",
            )
        )

        context["cart_count"] = cart.total_items
        context["cart_subtotal"] = cart.subtotal

    except Exception as e:
        print("Cart Context Error:", e)

    # -------------------------
    # WISHLIST
    # -------------------------
    try:
        wishlist = get_wishlist(request)

        context["wishlist_count"] = wishlist.items.count()

    except Exception as e:
        print("Wishlist Context Error:", e)

    return context
def get_cart(request):
    """
    Returns the current user's cart.
    """

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={
            "user": None,
        },
    )

    return cart


def get_wishlist(request):
    """
    Returns the current user's wishlist.
    Supports logged in and anonymous users.
    """

    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(
            user=request.user
        )
        return wishlist

    if not request.session.session_key:
        request.session.create()

    wishlist, _ = Wishlist.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={
            "user": None,
        },
    )

    return wishlist
from django.conf import settings

def google_client(request):
    return {
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    }