from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

from .models import Product, Category, Order, OrderItem, Review, ProductVariant


class SmartComputersAdminSite(AdminSite):
    site_header = "SmartComputersKE Admin"
    site_title = "SmartComputersKE Admin"
    index_title = "Dashboard"

    # ---------------------------------------------------------
    # Header context available on every admin page (notifications)
    # ---------------------------------------------------------
    def each_context(self, request):
        context = super().each_context(request)
        notifications = self._get_notifications()
        context["sck_notifications"] = notifications
        context["sck_notification_count"] = len(notifications)
        return context

    def _get_notifications(self):
        notifications = []
        now = timezone.now()
        cutoff = now - timedelta(days=2)

        for o in Order.objects.filter(created_at__gte=cutoff).order_by("-created_at")[:5]:
            notifications.append({
                "title": f"New order {o.order_id}",
                "time_ago": self._time_ago(o.created_at),
                "url": f"/admin/app/order/{o.id}/change/",
                "icon": self._icon("cart"),
                "sort": o.created_at,
            })

        for r in Review.objects.filter(created_at__gte=cutoff).order_by("-created_at")[:5]:
            notifications.append({
                "title": f"New review on {r.product.name}",
                "time_ago": self._time_ago(r.created_at),
                "url": f"/admin/app/review/{r.id}/change/",
                "icon": self._icon("star"),
                "sort": r.created_at,
            })

        for v in ProductVariant.objects.filter(stock__lte=5, stock__gt=0, active=True).select_related("product")[:5]:
            notifications.append({
                "title": f"Low stock: {v.product.name} ({v.stock} left)",
                "time_ago": "Ongoing",
                "url": f"/admin/app/productvariant/{v.id}/change/",
                "icon": self._icon("warning"),
                "sort": now,
            })

        notifications.sort(key=lambda n: n["sort"], reverse=True)
        for n in notifications:
            n.pop("sort", None)
        return notifications[:8]

    def _time_ago(self, dt):
        seconds = (timezone.now() - dt).total_seconds()
        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            return f"{int(seconds // 60)}m ago"
        if seconds < 86400:
            return f"{int(seconds // 3600)}h ago"
        return f"{int(seconds // 86400)}d ago"

    def _icon(self, name):
        icons = {
            "cart": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>',
            "star": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
            "warning": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        }
        return icons.get(name, "")

    # ---------------------------------------------------------
    # Dashboard homepage stats + chart data
    # ---------------------------------------------------------
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self._get_dashboard_stats())
        return super().index(request, extra_context=extra_context)

    def _get_dashboard_stats(self):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0
        monthly_revenue = Order.objects.filter(
            created_at__gte=month_start
        ).aggregate(total=Sum("total_amount"))["total"] or 0

        active_deals = ProductVariant.objects.filter(
            active=True, discount_price__isnull=False,
        ).filter(
            Q(discount_start__isnull=True) | Q(discount_start__lte=now),
            Q(discount_end__isnull=True) | Q(discount_end__gte=now),
        ).count()

        return {
            "stat_total_products": Product.objects.count(),
            "stat_total_categories": Category.objects.count(),
            "stat_total_orders": Order.objects.count(),
            "stat_total_customers": User.objects.filter(is_staff=False).count(),
            "stat_total_reviews": Review.objects.count(),
            "stat_total_revenue": float(total_revenue),
            "stat_monthly_revenue": float(monthly_revenue),
            "stat_low_stock": ProductVariant.objects.filter(stock__lte=5, stock__gt=0, active=True).count(),
            "stat_out_of_stock": ProductVariant.objects.filter(stock=0, active=True).count(),
            "stat_active_deals": active_deals,
            # Passed as a dict (not pre-serialized) so the template can use
            # the |json_script filter, which safely escapes it for embedding.
            "chart_data": self._get_chart_data(),
        }

    def _get_chart_data(self):
        now = timezone.now()

        # Build 6 rolling month buckets ending this month
        cursor = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        buckets = [cursor]
        for _ in range(5):
            prev_month = cursor.month - 1 or 12
            prev_year = cursor.year - 1 if cursor.month == 1 else cursor.year
            cursor = cursor.replace(year=prev_year, month=prev_month)
            buckets.append(cursor)
        buckets.reverse()

        def month_end(start):
            nm = start.month + 1 if start.month < 12 else 1
            ny = start.year + 1 if start.month == 12 else start.year
            return start.replace(year=ny, month=nm)

        months, sales_counts, revenue_totals, reg_counts = [], [], [], []
        for start in buckets:
            end = month_end(start)
            bucket_orders = Order.objects.filter(created_at__gte=start, created_at__lt=end)
            months.append(start.strftime("%b"))
            sales_counts.append(bucket_orders.count())
            revenue_totals.append(float(bucket_orders.aggregate(total=Sum("total_amount"))["total"] or 0))
            reg_counts.append(
                User.objects.filter(date_joined__gte=start, date_joined__lt=end, is_staff=False).count()
            )

        cat_data = list(
            Category.objects.annotate(product_total=Count("products"))
            .values("name", "product_total").order_by("-product_total")[:8]
        )

        top_products = list(
            OrderItem.objects.values("product__name")
            .annotate(total_sold=Sum("quantity")).order_by("-total_sold")[:8]
        )

        week_labels, week_counts = [], []
        for i in range(6, -1, -1):
            day = (now - timedelta(days=i)).date()
            week_labels.append(day.strftime("%a"))
            week_counts.append(Order.objects.filter(created_at__date=day).count())

        return {
            "months": months,
            "monthly_sales": sales_counts,
            "monthly_revenue": revenue_totals,
            "category_labels": [c["name"] for c in cat_data],
            "category_counts": [c["product_total"] for c in cat_data],
            "top_product_labels": [p["product__name"] for p in top_products],
            "top_product_counts": [p["total_sold"] for p in top_products],
            "registration_labels": months,
            "registration_counts": reg_counts,
            "week_labels": week_labels,
            "week_counts": week_counts,
        }


# Patch the existing default admin.site singleton in place.
# This preserves every @admin.register(...) call already made in
# app/admin.py — nothing gets re-registered, nothing gets replaced.
admin.site.__class__ = SmartComputersAdminSite
admin.site.site_header = "SmartComputersKE Admin"
admin.site.site_title = "SmartComputersKE Admin"
admin.site.index_title = "Dashboard"