from django.contrib import admin
from django.urls import path
from django.contrib.admin import AdminSite
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import *
from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductVariant,
    Specification,
    
    VariantSpecification,
    Review,
)

class SmartComputersAdminSite(AdminSite):
    site_header = "SmartComputersKE Administration"
    site_title = "SmartComputersKE"
    index_title = "Dashboard"

    def each_context(self, request):
        context = super().each_context(request)

        from .models import (
            Product,
            Category,
            Brand,
            Order,
            Review,
            Cart,
            Wishlist,
        )

        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        total_brands = Brand.objects.count()
        total_orders = Order.objects.count()
        total_customers = User.objects.count()

        revenue = (
            Order.objects.aggregate(
                total=Sum("total_amount")
            )["total"] or 0
        )

        pending_orders = Order.objects.filter(
            status="pending"
        ).count()

        processing_orders = Order.objects.filter(
            status="processing"
        ).count()

        shipping_orders = Order.objects.filter(
            status="shipping"
        ).count()

        delivered_orders = Order.objects.filter(
            status="delivered"
        ).count()

        low_stock = ProductVariant.objects.filter(
            stock__lte=5,
            active=True
        ).count()

        recent_orders = (
            Order.objects
            .order_by("-created_at")[:8]
        )

        latest_reviews = (
            Review.objects
            .select_related("product")
            .order_by("-created_at")[:6]
        )

        best_categories = (
            Category.objects
            .annotate(total=Count("products"))
            .order_by("-total")[:5]
        )

        context.update({

            "products": total_products,

            "categories": total_categories,

            "brands": total_brands,

            "orders": total_orders,

            "customers": total_customers,

            "revenue": revenue,

            "pending_orders": pending_orders,

            "processing_orders": processing_orders,

            "shipping_orders": shipping_orders,

            "delivered_orders": delivered_orders,

            "low_stock": low_stock,

            "recent_orders": recent_orders,

            "latest_reviews": latest_reviews,

            "best_categories": best_categories,

        })

        return context
# ==========================
# CATEGORY  ->  its own Specification *names*
# ==========================

class SpecificationInline(admin.TabularInline):
    """
    Lets you add/edit/delete/reorder the spec names that belong
    to this category (e.g. Laptop -> RAM, Processor, Storage, Generation;
    Monitor -> Display, Resolution, Curved, Panel Type).
    No code changes ever needed to add a new spec — just add it here.
    """
    model = Specification
    extra = 1
    fields = ("name", "position")
    ordering = ("position", "name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SpecificationInline]

    def product_count(self, obj):
        return obj.product_count
    product_count.short_description = "Products"


# ==========================
# BRAND
# ==========================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ==========================
# SPECIFICATION  ->  its own allowed Values
# ==========================



# ==========================
# PRODUCT IMAGES INLINE (gallery)
# ==========================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ==========================
# PRODUCT VARIANTS INLINE (on Product page)
# This is where price / discount / stock / sku is actually set —
# Product itself only proxies to the first (default) variant.
# ==========================

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("sku", "image", "price", "discount_price", "discount_start", "discount_end", "stock", "active")


# ==========================
# REVIEWS INLINE — moderate reviews directly from the product page
# ==========================

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ("customer_name", "rating", "verified", "comment", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name", "category", "brand", "condition",
        "featured", "new_arrival", "trending", "active",
    )
    list_filter = (
        "category", "brand", "condition",
        "featured", "new_arrival",  "trending", "active",
    )
    search_fields = ("name", "brand__name", "category__name")
    readonly_fields = ("created", "updated")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "category", "brand", "condition")}),
        ("Images", {"fields": ("image",)}),
        ("Descriptions", {"fields": ("short_description", "description")}),
        ("Warranty & Pricing", {"fields": ("warranty", "vat_inclusive")}),
        ("Homepage", {"fields": ("featured", "new_arrival",  "trending", "active")}),
        ("Dates", {"fields": ("created", "updated")}),
    )

    inlines = [ProductVariantInline, ProductImageInline, ReviewInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "id")
    search_fields = ("product__name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "product", "rating", "verified", "created_at")
    list_filter = ("verified", "rating", "product__category")
    search_fields = ("customer_name", "product__name", "comment")
    readonly_fields = ("created_at",)


# ==========================
# VARIANT SPECIFICATIONS
# The dynamic, cascading part: Specification choices are filtered
# to the variant's product's category, and Value choices are
# filtered to the chosen Specification, all via AJAX + JS below.
# ==========================

class VariantSpecificationInline(admin.TabularInline):
    model = VariantSpecification
    extra = 8
    fields = (
        "specification",
        "value",
    )  # keep plain <select> so our JS can repopulate options

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [VariantSpecificationInline]

    list_display = ("product", "sku", "price", "discount_price", "stock", "active")
    list_filter = ("product__category", "active")
    search_fields = ("product__name", "sku")
    inlines = [VariantSpecificationInline]

    class Media:
        js = ("admin/js/variant_specs.js",)

    # ---- AJAX endpoints used by admin/js/variant_specs.js ----

    def get_urls(self):
        custom_urls = [
            path(
                "ajax/specifications/",
                self.admin_site.admin_view(self.ajax_specifications),
                name="products_productvariant_ajax_specifications",
            ),
            path(
                "ajax/specification-values/",
                self.admin_site.admin_view(self.ajax_specification_values),
                name="products_productvariant_ajax_specification_values",
            ),
        ]
        return custom_urls + super().get_urls()

    def ajax_specifications(self, request):
        """Return the specifications that belong to the given product's category."""
        product_id = request.GET.get("product_id")
        results = []
        if product_id:
            product = Product.objects.filter(pk=product_id).select_related("category").first()
            if product and product.category_id:
                specs = Specification.objects.filter(
                    category=product.category
                ).order_by("position", "name")
                results = [{"id": s.id, "text": s.name} for s in specs]
        return JsonResponse({"results": results})

    def ajax_specification_values(self, request):
        """Return the allowed values for the given specification."""
        specification_id = request.GET.get("specification_id")
        results = []
        if specification_id:
            values = SpecificationValue.objects.filter(
                specification_id=specification_id
            ).order_by("position")
            results = [{"id": v.id, "text": v.value} for v in values]
        return JsonResponse({"results": results})


@admin.register(VariantSpecification)
class VariantSpecificationAdmin(admin.ModelAdmin):
    list_display = ("variant", "specification", "value")
    list_filter = ("variant__product__category",)
    search_fields = (
        "variant__product__name",
        "specification__name",
        "value__value",
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "total_items",
        "subtotal",
        "updated",
    )

    inlines = [
        CartItemInline,
    ]
class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "created",
    )

    inlines = [
        WishlistItemInline,
    ]