from datetime import timedelta

from django.db.models import Count, Sum, Q
from django.utils import timezone

from app.models import (
    AnalyticsEvent,
    Product,
    Category,
    Brand,
    Order,
    OrderItem,
)
class DashboardAnalytics:

    @staticmethod
    def today():

        return timezone.now().date()
    @classmethod
    def total_views(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.VIEW
        ).count()
    @classmethod
    def today_views(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.VIEW,
            created_at__date=cls.today(),
        ).count()
    @classmethod
    def week_views(cls):

        start = timezone.now() - timedelta(days=7)

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.VIEW,
            created_at__gte=start,
        ).count()
    @classmethod
    def month_views(cls):

        now = timezone.now()

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.VIEW,
            created_at__year=now.year,
            created_at__month=now.month,
        ).count()
    @classmethod
    def revenue(cls):

        revenue = Order.objects.aggregate(
            total=Sum("grand_total")
        )

        return revenue["total"] or 0
    @classmethod
    def total_orders(cls):

        return Order.objects.count()
    @classmethod
    def total_products(cls):

        return Product.objects.count()
    @classmethod
    def total_categories(cls):

        return Category.objects.count()
    @classmethod
    def total_brands(cls):

        return Brand.objects.count()
    @classmethod
    def cart_additions(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.CART
        ).count()
    @classmethod
    def checkout_count(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.CHECKOUT
        ).count()
    @classmethod
    def purchases(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.PURCHASE
        ).count()
    @classmethod
    def wishlists(cls):

        return AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.WISHLIST
        ).count()
    @classmethod
    def conversion_rate(cls):

        views = cls.total_views()

        purchases = cls.purchases()

        if views == 0:
            return 0

        return round((purchases / views) * 100, 2)
    @classmethod
    def most_viewed_products(cls):

        return (
            Product.objects
            .annotate(
                total_views=Count(
                    "analytics_events",
                    filter=Q(
                        analytics_events__event_type=AnalyticsEvent.VIEW
                    )
                )
            )
            .order_by("-total_views")[:10]
        )
    @classmethod
    def most_purchased_products(cls):

        return (
            Product.objects
            .annotate(
                units_sold=Sum(
                    "orderitem__quantity"
                )
            )
            .order_by("-units_sold")[:10]
        )
    @classmethod
    def highest_revenue_products(cls):

        return (
            Product.objects
            .annotate(
                revenue=Sum(
                    "orderitem__total"
                )
            )
            .order_by("-revenue")[:10]
        )
    @classmethod
    def lowest_conversion_products(cls):

        products = []

        for product in Product.objects.all():

            views = product.analytics_events.filter(
                event_type=AnalyticsEvent.VIEW
            ).count()

            purchases = product.analytics_events.filter(
                event_type=AnalyticsEvent.PURCHASE
            ).count()

            if views > 20 and purchases == 0:
                products.append(product)

        return products
    @classmethod
    def fast_moving_products(cls):

        return (
            Product.objects
            .annotate(
                sold=Sum(
                    "orderitem__quantity"
                )
            )
            .order_by("-sold")[:20]
        )