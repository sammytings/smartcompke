"""
dashboard.py
------------
Put this file in the SAME app as your models (next to admin.py/models.py) —
e.g. `products/dashboard.py`.

It gathers all the numbers shown on the new admin homepage and wires them
in via Unfold's DASHBOARD_CALLBACK (see settings_snippet.py).

IMPORTANT NOTE ON "SALES / REVENUE / RECENT ORDERS"
----------------------------------------------------
Your current models.py has no Order/Checkout model — only Cart and
CartItem. There's no completed-purchase history yet, so there's no way
to show *real* sales figures.

To keep the dashboard honest instead of showing fake numbers, this file
treats "Recent Orders" as "Recent Cart Activity" (items added to carts)
and "Revenue" as "Value currently sitting in active carts" — both
clearly labeled as such in the template.

The moment you add a real Order/OrderItem model (recommended once you
build checkout), just rewrite `sales_stats()` below to query that model
instead — nothing else in this file needs to change.
"""

from datetime import timedelta

from django.db.models import Count, Avg
from django.utils import timezone

from .models import (
    Category,
    Product,
    ProductVariant,
    CartItem,
    WishlistItem,
    Review,
)

LOW_STOCK_THRESHOLD = 5


def sales_stats():
    """Proxy 'sales' data built from live cart activity (no Order model exists yet)."""
    items = (
        CartItem.objects.filter(saved_for_later=False)
        .select_related("product", "variant", "cart__user")
        .order_by("-added")
    )
    revenue_in_carts = sum((item.subtotal for item in items), 0)
    return {
        "revenue_in_carts": revenue_in_carts,
        "active_cart_items_count": items.count(),
        "recent_activity": items[:8],
    }


def low_stock_variants(threshold=LOW_STOCK_THRESHOLD):
    return (
        ProductVariant.objects.filter(active=True, stock__lte=threshold)
        .select_related("product")
        .order_by("stock")[:10]
    )


def out_of_stock_count():
    return ProductVariant.objects.filter(active=True, stock=0).count()


def top_products(limit=6):
    return (
        Product.objects.filter(active=True)
        .annotate(
            reviews_count=Count("reviews", distinct=True),
            avg_rating=Avg("reviews__rating"),
            times_wishlisted=Count("wishlistitem", distinct=True),
        )
        .order_by("-reviews_count", "-avg_rating")[:limit]
    )


def recent_reviews(limit=6):
    return Review.objects.select_related("product").order_by("-created_at")[:limit]


def cart_wishlist_activity():
    since = timezone.now() - timedelta(days=7)
    return {
        "cart_adds_7d": CartItem.objects.filter(added__gte=since).count(),
        "wishlist_adds_7d": WishlistItem.objects.filter(created__gte=since).count(),
        "top_wishlisted": Product.objects.annotate(
            wishlist_count=Count("wishlistitem")
        )
        .filter(wishlist_count__gt=0)
        .order_by("-wishlist_count")[:5],
    }


def dashboard_callback(request, context):
    """
    Registered in settings.py as:
        UNFOLD = {"DASHBOARD_CALLBACK": "products.dashboard.dashboard_callback"}
    (adjust "products" to whatever your app is actually called)
    """
    context.update(
        {
            "sales": sales_stats(),
            "low_stock": low_stock_variants(),
            "out_of_stock_count": out_of_stock_count(),
            "top_products": top_products(),
            "recent_reviews": recent_reviews(),
            "activity": cart_wishlist_activity(),
            "total_products": Product.objects.filter(active=True).count(),
            "total_categories": Category.objects.count(),
            "low_stock_threshold": LOW_STOCK_THRESHOLD,
        }
    )
    return context