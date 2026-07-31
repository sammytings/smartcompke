from django.db.models import Count, Sum, Q

from app.models import Product, AnalyticsEvent
def most_viewed(limit=20):

    return (
        Product.objects
        .annotate(
            total_views=Count(
                "analytics_events",
                filter=Q(
                    analytics_events__event_type=AnalyticsEvent.VIEW
                ),
            )
        )
        .order_by("-total_views")[:limit]
    )
def most_added_to_cart(limit=20):

    return (
        Product.objects
        .annotate(
            carts=Count(
                "analytics_events",
                filter=Q(
                    analytics_events__event_type=AnalyticsEvent.CART
                ),
            )
        )
        .order_by("-carts")[:limit]
    )
def most_wishlisted(limit=20):

    return (
        Product.objects
        .annotate(
            wishlists=Count(
                "analytics_events",
                filter=Q(
                    analytics_events__event_type=AnalyticsEvent.WISHLIST
                ),
            )
        )
        .order_by("-wishlists")[:limit]
    )
def most_checked_out(limit=20):

    return (
        Product.objects
        .annotate(
            checkouts=Count(
                "analytics_events",
                filter=Q(
                    analytics_events__event_type=AnalyticsEvent.CHECKOUT
                ),
            )
        )
        .order_by("-checkouts")[:limit]
    )
from django.db.models import Sum

from app.models import Product
def best_selling(limit=20):

    return (
        Product.objects
        .annotate(
            sold=Sum("orderitem__quantity")
        )
        .order_by("-sold")[:limit]
    )