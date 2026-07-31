from decimal import Decimal

from django.db.models import F
from django.utils import timezone

from app.models import ProductAnalytics


class AnalyticsService:

    @staticmethod
    def get(product):

        analytics, created = ProductAnalytics.objects.get_or_create(
            product=product
        )

        return analytics

    @staticmethod
    def record_view(product):

        ProductAnalytics.objects.update_or_create(
            product=product,
            defaults={
                "last_viewed": timezone.now()
            }
        )

        ProductAnalytics.objects.filter(
            product=product
        ).update(
            total_views=F("total_views") + 1
        )

    @staticmethod
    def record_wishlist(product):

        ProductAnalytics.objects.get_or_create(
            product=product
        )

        ProductAnalytics.objects.filter(
            product=product
        ).update(
            wishlist_adds=F("wishlist_adds") + 1
        )

    @staticmethod
    def record_cart(product, quantity=1):

        ProductAnalytics.objects.get_or_create(
            product=product
        )

        ProductAnalytics.objects.filter(
            product=product
        ).update(
            cart_adds=F("cart_adds") + quantity
        )

    @staticmethod
    def remove_cart(product, quantity=1):

        analytics = AnalyticsService.get(product)

        analytics.cart_adds = max(
            analytics.cart_adds - quantity,
            0
        )

        analytics.save()

    @staticmethod
    def record_checkout(product, quantity=1):

        ProductAnalytics.objects.get_or_create(
            product=product
        )

        ProductAnalytics.objects.filter(
            product=product
        ).update(
            checkout_count=F("checkout_count") + quantity
        )

    @staticmethod
    def record_sale(product, quantity, amount):

        analytics = AnalyticsService.get(product)

        analytics.total_sales += quantity

        analytics.total_revenue += Decimal(amount)

        analytics.save()

    @staticmethod
    def record_abandoned(product, quantity=1):

        ProductAnalytics.objects.get_or_create(
            product=product
        )

        ProductAnalytics.objects.filter(
            product=product
        ).update(
            abandoned_carts=F("abandoned_carts") + quantity
        )

    @staticmethod
    def track(
        request,
        event_type,
        product,
        variant=None,
        quantity=1,
        revenue=Decimal("0.00"),
    ):

        from app.models import AnalyticsEvent

        if event_type == AnalyticsEvent.VIEW:

            AnalyticsService.record_view(
                product
            )

        elif event_type == AnalyticsEvent.CART:

            AnalyticsService.record_cart(
                product,
                quantity,
            )

        elif event_type == AnalyticsEvent.WISHLIST:

            AnalyticsService.record_wishlist(
                product
            )

        elif event_type == AnalyticsEvent.CHECKOUT:

            AnalyticsService.record_checkout(
                product,
                quantity,
            )

        elif event_type == AnalyticsEvent.PURCHASE:

            AnalyticsService.record_sale(
                product,
                quantity,
                revenue,
            )