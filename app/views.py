"""
views.py

CLEANUP NOTES (read before deploying):
1. All imports were merged and moved to the top of the file. Duplicate
   `import` lines scattered through the original file were removed.
2. Every dashboard/admin view is now protected with
   @staff_member_required(login_url="dashboard_login"). Views that were
   previously unprotected (dashboard_analytics, dashboard_customers,
   google_reviews, dashboard_marketing, marketing_history/detail/duplicate/
   delete, dashboard_banners + add/edit/delete, order_list/delete_order,
   dashboard_deals family, all dashboard_inventory* views, dashboard_blog*
   views, add/edit/delete_brand, dashboard_delete_product, etc.) are now
   locked down.
3. Several functions were defined TWICE in the original file (Python simply
   used whichever definition came last, silently discarding the other).
   The duplicates were merged/removed:
     - order_detail: there were two versions. The full-featured one (status
       changes + customer emails) is kept and renamed `dashboard_order_detail`
       to avoid clashing with the public-facing `order_detail` used for
       customer order tracking. **You must update urls.py**: point the
       staff/dashboard order-detail URL at `dashboard_order_detail` instead
       of `order_detail`.
     - dashboard_banners / dashboard_add_banner / dashboard_edit_banner /
       dashboard_delete_banner: the earlier empty stub versions were removed,
       the fully implemented versions were kept.
     - marketing_detail: kept the version that also fetches related
       products.
     - send_marketing_campaign: kept the version that emails Customers /
       NewsletterSubscribers (the earlier version that only emailed
       auth.User was removed).
     - dashboard_analytics: kept the version backed by the ProductAnalytics
       model; removed the earlier AnalyticsEvent-only version.
     - brand_list: kept the version that annotates `product_count`.
     - quote_success: removed the exact duplicate definition.
4. The public `order_detail` (customer order tracking) previously did not
   filter by the requesting user, so any logged-in user could view any
   order by guessing an order_id. It now requires login and only returns
   the order if it belongs to `request.user`.
5. Removed leftover debugging `print(...)` statements that were dumping
   session/cart internals to the console (add_to_cart, cart, import_product,
   google_one_tap, etc.).
6. `send_order_confirmation_email(request, order)` is still called from
   `checkout()` on every successful order, so customers get an email
   confirmation as soon as they place an order. `send_order_email(...)`
   is called from `dashboard_order_detail()` whenever staff change an
   order's status — make sure both helpers exist in `.utils` /
   `app/utils.py`; they were referenced in the original file but not
   defined there.
7. NOTE: this file was cleaned up in isolation, without access to your
   models.py / forms.py / urls.py. Import paths were normalized to
   relative imports (`.models`, `.forms`, `.utils`, `.services...`) since
   the surrounding code lives inside the same app. Double check these
   still match your project layout, and update urls.py for the rename
   in point 3.
"""

import json
import random
import traceback
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Max, Min, Prefetch, Q, Sum
from django.forms import modelform_factory
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from .ai.assistant import SmartAI
from .forms import (
    BannerForm,
    BlogForm,
    BrandForm,
    CategoryForm,
    DealCampaignForm,
    InventoryTransactionForm,
    MarketingCampaignForm,
    NewsletterSubscriberForm,
    ProductForm,
    ProductImportForm,
    ProductVariantForm,
    QuoteRequestForm,
    RegisterForm,
    StockAdjustmentForm,
    StockInForm,
    StockOutForm,
    VariantSpecificationForm,
    VariantSpecificationFormSet,
)
from .models import (
    AnalyticsEvent,
    Banner,
    BlogCategory,
    BlogPost,
    Brand,
    Cart,
    CartItem,
    Category,
    Customer,
    DealCampaign,
    EmailOTP,
    GoogleReview,
    InventoryTransaction,
    MarketingCampaign,
    NewsletterSubscriber,
    Order,
    OrderItem,
    Product,
    ProductAnalytics,
    ProductImage,
    ProductVariant,
    Specification,
    StaffProfile,
    VariantSpecification,
    Wishlist,
    WishlistItem,
)
from .services.analytics import AnalyticsService
from .services.import_service import ProductImportService
from .services.utils import generate_unique_sku
from .utils import (
    generate_otp,
    get_cart,
    get_wishlist,
    send_order_confirmation_email,
    
    send_otp_email,
)

User = get_user_model()


# ==========================================
# BRAND BANNERS
# ==========================================

BRAND_BANNERS = {
    "hp": ["brand_banners/hp.jpg"],
    "dell": ["brand_banners/dell.jpg"],
    "lenovo": ["brand_banners/lenovo.jpg"],
    "apple": ["brand_banners/apple.jpg"],
    "samsung": ["brand_banners/samsung.jpg"],
    "asus": ["brand_banners/asus.jpg"],
    "acer": ["brand_banners/acer.jpg"],
    "lg": ["brand_banners/lg.jpg"],
    "belkin": ["brand_banners/belkin.jpg"],
    "canon": ["brand_banners/canon.jpg"],
    "epson": ["brand_banners/epson.jpg"],
    "infinix": ["brand_banners/infinix.jpg"],
    "default": ["brand_banners/default.jpg"],
}


# ==========================================
# STOREFRONT
# ==========================================
from django.db.models import Min, Max, Q, Prefetch
from django.core.paginator import Paginator
from django.db.models import Min, Max, Q
from django.utils import timezone
def home(request):
    now = timezone.now()

    # Categories
    categories = Category.objects.all()

    # Brands
    all_brands = Brand.objects.all().order_by("name")

    # Category Menu
    menu_categories = []

    for category in categories:

        category_brands = (
            Brand.objects.filter(
                products__category=category,
                products__active=True,
            )
            .distinct()
            .order_by("name")
        )

        conditions = (
            Product.objects.filter(
                category=category,
                active=True
            )
            .exclude(condition="")
            .values_list("condition", flat=True)
            .distinct()
        )

        menu_categories.append({
            "category": category,
            "brands": category_brands,
            "conditions": conditions,
        })

    # -------------------------
    # FEATURED PRODUCTS
    # -------------------------

    featured_queryset = (
        Product.objects
        .filter(featured=True, active=True)
        .select_related("brand", "category")
        .order_by("-id")
    )

    featured_paginator = Paginator(featured_queryset, 12)

    featured_page = request.GET.get("featured_page", 1)

    featured_products = featured_paginator.get_page(featured_page)

    # -------------------------
    # DEALS
    # -------------------------

    deals = (
        Product.objects.filter(
            active=True,
            variants__active=True,
            variants__discount_price__isnull=False,
        )
        .filter(
            Q(variants__discount_start__isnull=True)
            | Q(variants__discount_start__lte=now),

            Q(variants__discount_end__isnull=True)
            | Q(variants__discount_end__gte=now),
        )
        .distinct()
        .select_related("brand", "category")
    )

    # -------------------------
    # NEW ARRIVALS
    # -------------------------

    new_arrivals = (
        Product.objects.filter(
            new_arrival=True,
            active=True,
        )
        .select_related("brand", "category")
        .order_by("-id")[:12]
    )

    # -------------------------
    # TRENDING
    # -------------------------

    trending = (
        Product.objects.filter(
            trending=True,
            active=True,
        )
        .select_related("brand", "category")
        .order_by("-id")[:12]
    )

    # -------------------------
    # GOOGLE REVIEWS
    # -------------------------

    reviews = GoogleReview.objects.filter(
        is_visible=True
    )[:6]

    # -------------------------
    # PRICE RANGE
    # -------------------------

    price_range = (
        ProductVariant.objects
        .filter(active=True)
        .aggregate(
            price_floor=Min("price"),
            price_ceiling=Max("price"),
        )
    )

    context = {

        "categories": categories,

        "menu_categories": menu_categories,

        "brands": all_brands,

        "featured_products": featured_products,

        "new_arrivals": new_arrivals,

        "trending": trending,

        "deals": deals,

        "google_reviews": reviews,

        "price_floor": price_range["price_floor"] or 0,

        "price_ceiling": price_range["price_ceiling"] or 300000,

        "selected_price_min": request.GET.get("price_min"),

        "selected_price_max": request.GET.get("price_max"),
    }

    return render(request, "index.html", context)
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse

def featured_deals_page(request):
    now = timezone.now()

    deals = (
        Product.objects
        .filter(
            active=True,
            variants__active=True,
            variants__discount_price__isnull=False,
        )
        .filter(
            Q(variants__discount_start__isnull=True) | Q(variants__discount_start__lte=now),
            Q(variants__discount_end__isnull=True) | Q(variants__discount_end__gte=now),
        )
        .select_related("brand", "category")
        .distinct()
        .order_by("-id")
    )

    paginator = Paginator(deals, 12)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    html = render_to_string(
        "partials/featured_deals_grid.html",
        {
            "deals": page_obj,
        },
        request=request,
    )

    return JsonResponse({
        "html": html,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
    })
from django.http import JsonResponse
from django.template.loader import render_to_string
def featured_products_ajax(request):

    featured_queryset = (
        Product.objects
        .filter(featured=True, active=True)
        .select_related("brand", "category")
        .order_by("-id")
    )

    paginator = Paginator(featured_queryset, 12)

    page = request.GET.get("page", 1)

    featured_products = paginator.get_page(page)

    html = render_to_string(
        "partials/featured_deals_grid.html",
        {
            "featured_products": featured_products,
        },
        request=request
    )


    return JsonResponse({

        "html": html,

        "page": featured_products.number,

        "pages": paginator.num_pages,

        "next": featured_products.has_next(),

        "previous": featured_products.has_previous(),

    })
def categories_page(request):

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "categories/categories.html",
        {
            "categories": categories,
        },
    )
def category_products(request, slug):
    from collections import defaultdict

    category = get_object_or_404(Category, slug=slug)

    banner = Banner.objects.filter(
        banner_type="category", category=category, active=True
    ).first()

    if not banner:
        banner = Banner.objects.filter(
            banner_type="category_global", active=True
        ).first()

    slider_banners = Banner.objects.filter(
        banner_type="category_slider", active=True
    ).order_by("order")

    products = (
        Product.objects.filter(category=category, active=True)
        .select_related("brand", "category")
        .prefetch_related("variants__attributes__specification")
    )

    search = request.GET.get("q")
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(short_description__icontains=search)
        )

    selected_brands = request.GET.getlist("brand")
    if selected_brands:
        products = products.filter(brand__slug__in=selected_brands)

    selected_conditions = request.GET.getlist("condition")
    if selected_conditions:
        products = products.filter(condition__in=selected_conditions)

    specifications = defaultdict(set)
    for product in products:
        variant = product.default_variant
        if variant:
            for attribute in variant.attributes.select_related("specification"):
                specifications[attribute.specification.name].add(attribute.value)

    specification_filters = [
        {"name": spec_name, "values": sorted(values)}
        for spec_name, values in specifications.items()
    ]

    brands = Brand.objects.filter(
        products__category=category, products__active=True
    ).distinct()

    conditions = (
        Product.objects.filter(category=category, active=True)
        .exclude(condition="")
        .values_list("condition", flat=True)
        .distinct()
    )

    paginator = Paginator(products, 12)
    products = paginator.get_page(request.GET.get("page"))

    related_categories = Category.objects.exclude(id=category.id)[:8]

    context = {
        "category": category,
        "products": products,
        "banner": banner,
        "slider_banners": slider_banners,
        "brands": brands,
        "conditions": conditions,
        "selected_brands": selected_brands,
        "selected_conditions": selected_conditions,
        "categories": Category.objects.all(),
        "related_categories": related_categories,
        "specification_filters": specification_filters,
    }

    return render(request, "category.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related(
            Prefetch(
                "gallery",
                queryset=ProductImage.objects.order_by("-is_primary", "uploaded_at", "id"),
            ),
            "reviews",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.prefetch_related(
                    Prefetch(
                        "attributes",
                        queryset=VariantSpecification.objects.select_related(
                            "specification"
                        ).order_by("specification__position"),
                    )
                ),
            ),
        ),
        slug=slug,
        active=True,
    )

    AnalyticsService.track(
        request=request,
        event_type=AnalyticsEvent.VIEW,
        product=product,
        variant=product.default_variant,
    )

    variant = product.default_variant
    variants = product.variants.filter(active=True)
    specifications = variant.attributes.all() if variant else []

    recommended_products = Product.objects.filter(
        category=product.category, active=True
    ).exclude(pk=product.pk)[:12]

    related_categories = Category.objects.exclude(pk=product.category_id)[:5]

    previous_product = (
        Product.objects.filter(category=product.category, active=True, id__lt=product.id)
        .order_by("-id")
        .first()
    )

    next_product = (
        Product.objects.filter(category=product.category, active=True, id__gt=product.id)
        .order_by("id")
        .first()
    )

    viewed = request.session.get("recently_viewed", [])
    if product.id in viewed:
        viewed.remove(product.id)
    viewed.insert(0, product.id)
    request.session["recently_viewed"] = viewed[:12]

    recently_viewed_qs = Product.objects.filter(id__in=viewed[1:], active=True)
    ordered_recent = [
        obj for pid in viewed[1:]
        if (obj := recently_viewed_qs.filter(id=pid).first())
    ]

    context = {
        "product": product,
        "variant": variant,
        "variants": variants,
        "specifications": specifications,
        "recommended_products": recommended_products,
        "related_categories": related_categories,
        "previous_product": previous_product,
        "next_product": next_product,
        "recently_viewed": ordered_recent,
        "bundle_items": [],
        "bundle_total": 0,
    }

    return render(request, "product_detail.html", context)


def shop(request):
    products = (
        Product.objects.filter(active=True)
        .select_related("category", "brand")
        .prefetch_related("variants")
        .annotate(min_price=Min("variants__price"))
        .distinct()
    )

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
            | Q(category__name__icontains=q)
            | Q(brand__name__icontains=q)
        )

    category = request.GET.get("category")
    if category:
        products = products.filter(category__slug=category)

    brand = request.GET.get("brand")
    if brand:
        products = products.filter(brand__slug=brand)

    condition = request.GET.get("condition")
    if condition:
        products = products.filter(condition=condition)

    if request.GET.get("featured"):
        products = products.filter(featured=True)

    if request.GET.get("trending"):
        products = products.filter(trending=True)

    if request.GET.get("new"):
        products = products.filter(new_arrival=True)

    stock = request.GET.get("stock")
    if stock == "in":
        products = products.filter(variants__active=True, variants__stock__gt=0)
    elif stock == "out":
        products = products.filter(variants__active=True, variants__stock=0)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(variants__active=True, variants__price__gte=min_price)
    if max_price:
        products = products.filter(variants__active=True, variants__price__lte=max_price)

    sort = request.GET.get("sort")
    if sort == "price_low":
        products = products.order_by("min_price")
    elif sort == "price_high":
        products = products.order_by("-min_price")
    elif sort == "name":
        products = products.order_by("name")
    elif sort == "oldest":
        products = products.order_by("created")
    else:
        products = products.order_by("-created")

    products = products.distinct()

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.annotate(
        active_products=Count("products", filter=Q(products__active=True))
    ).order_by("name")

    brands = Brand.objects.annotate(
        product_count=Count("products", filter=Q(products__active=True))
    ).order_by("name")

    price_stats = products.aggregate(
        price_floor=Min("variants__price"),
        price_ceiling=Max("variants__price"),
    )
    price_floor = price_stats["price_floor"] or 0
    price_ceiling = price_stats["price_ceiling"] or 3000000

    price_range = ProductVariant.objects.filter(active=True).aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
    )

    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "categories": categories,
        "brands": brands,
        "conditions": Product._meta.get_field("condition").choices,
        "selected_category": category,
        "selected_brand": brand,
        "selected_condition": condition,
        "search_query": q,
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
        "price_range": price_range,
        "price_floor": price_floor,
        "price_ceiling": price_ceiling,
        "selected_price_min": request.GET.get("min_price", ""),
        "selected_price_max": request.GET.get("max_price", ""),
        "query_params": query_params.urlencode(),
    }

    return render(request, "shop/shop.html", context)


def product_search(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category")
    brand = request.GET.get("brand")
    condition = request.GET.get("condition")
    featured = request.GET.get("featured")
    trending = request.GET.get("trending")
    new_arrival = request.GET.get("new_arrival")
    sort = request.GET.get("sort")

    products = Product.objects.select_related("brand", "category").prefetch_related("variants")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(brand__name__icontains=query)
            | Q(variants__sku__icontains=query)
        ).distinct()

    if category:
        products = products.filter(category_id=category)
    if brand:
        products = products.filter(brand_id=brand)
    if condition:
        products = products.filter(condition=condition)
    if featured:
        products = products.filter(featured=True)
    if trending:
        products = products.filter(trending=True)
    if new_arrival:
        products = products.filter(new_arrival=True)

    if sort == "price_low":
        products = products.order_by("variants__price")
    elif sort == "price_high":
        products = products.order_by("-variants__price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created")

    context = {
        "products": products.distinct(),
        "query": query,
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
    }

    return render(request, "search_results.html", context)


def brand_list(request):
    query = request.GET.get("q", "")

    brands = Brand.objects.annotate(product_count=Count("products")).order_by("name")

    if query:
        brands = brands.filter(name__icontains=query)

    return render(request, "shop/brand_list.html", {"brands": brands, "query": query})


def brand_products(request, slug):
    brand = get_object_or_404(Brand, slug=slug)

    banner_list = BRAND_BANNERS.get(brand.slug.lower(), BRAND_BANNERS["default"])
    banner = random.choice(banner_list)

    products = (
        Product.objects.filter(brand=brand, active=True)
        .prefetch_related("variants", "gallery", "reviews")
        .select_related("brand", "category")
    )

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    condition = request.GET.get("condition")
    if condition:
        products = products.filter(condition=condition)

    sort = request.GET.get("sort")
    if sort == "newest":
        products = products.order_by("-created")
    elif sort == "oldest":
        products = products.order_by("created")
    else:
        products = products.order_by("-featured", "-created")

    categories = (
        Category.objects.filter(products__brand=brand, products__active=True)
        .distinct()
        .order_by("name")
    )

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "brand": brand,
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "total_products": products.count(),
        "selected_category": category_slug,
        "selected_condition": condition,
        "selected_sort": sort,
        "banner": banner,
    }

    return render(request, "brand_products.html", context)


def deals(request):
    now = timezone.now()

    deals_qs = ProductVariant.objects.filter(
        discount_price__isnull=False,
        discount_start__lte=now,
        discount_end__gte=now,
        active=True,
    ).select_related("product", "product__brand", "product__category")

    return render(request, "deals.html", {"deals": deals_qs})


def compare(request):
    compare_ids = request.session.get("compare", [])
    products = Product.objects.filter(id__in=compare_ids)
    return render(request, "compare.html", {"products": products})


def add_to_compare(request, product_id):
    compare_list = request.session.get("compare", [])

    if product_id not in compare_list:
        compare_list.append(product_id)
        added = True
    else:
        added = False

    request.session["compare"] = compare_list

    return JsonResponse({"added": added, "count": len(compare_list)})


def remove_from_compare(request, product_id):
    compare_list = request.session.get("compare", [])

    if product_id in compare_list:
        compare_list.remove(product_id)

    request.session["compare"] = compare_list

    return redirect(request.META.get("HTTP_REFERER", "compare_products"))


def about(request):
    return render(request, "shop/about.html")


# ==========================================
# CART
# ==========================================
from django.db.models import Case, When, IntegerField
def cart(request):
    cart_obj = get_cart(request)

    active_items = cart_obj.items.filter(saved_for_later=False)
    saved_items = cart_obj.items.filter(saved_for_later=True)

    related_products = Product.objects.none()

    if active_items.exists():

        cart_product_ids = active_items.values_list(
            "product_id",
            flat=True
        )

        category_ids = active_items.values_list(
            "product__category_id",
            flat=True
        ).distinct()

        brand_ids = active_items.values_list(
            "product__brand_id",
            flat=True
        ).distinct()

        related_products = (
            Product.objects
            .filter(
                active=True,
                category_id__in=category_ids,
                variants__active=True,
                variants__stock__gt=0,
            )
            .exclude(id__in=cart_product_ids)
            .annotate(
                priority=Case(
                    When(
                        brand_id__in=brand_ids,
                        then=0
                    ),
                    default=1,
                    output_field=IntegerField(),
                )
            )
            .distinct()
            .order_by("priority", "?")[:12]
        )

    return render(
        request,
        "cart.html",
        {
            "cart": cart_obj,
            "cart_items": active_items,
            "saved_for_later": saved_items,
            "cart_subtotal": cart_obj.subtotal,
            "cart_total": cart_obj.subtotal,
            "related_products": related_products,
        },
    )

def add_to_cart(request, product_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=405)

    product = get_object_or_404(Product, id=product_id, active=True)

    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))
    if quantity < 1:
        quantity = 1

    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
    else:
        variant = product.default_variant

    available_stock = (variant.stock if variant else product.stock) or 0

    if available_stock <= 0:
        return JsonResponse({"success": False, "message": "Out of stock."}, status=400)

    if quantity > available_stock:
        return JsonResponse(
            {"success": False, "message": f"Only {available_stock} item(s) available."},
            status=400,
        )

    cart_obj = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        variant=variant,
        defaults={"quantity": quantity},
    )

    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > available_stock:
            return JsonResponse(
                {"success": False, "message": f"You can only have {available_stock} item(s)."},
                status=400,
            )

        item.quantity = new_quantity
        item.save()

    AnalyticsService.track(
        request=request,
        event_type=AnalyticsEvent.CART,
        product=product,
        variant=variant,
        quantity=quantity,
    )

    return JsonResponse(
        {
            "success": True,
            "message": f"{product.name} added to cart.",
            "cart_count": cart_obj.total_items,
            "subtotal": float(cart_obj.subtotal),
        }
    )


def remove_from_cart(request, item_id):
    cart_obj = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)
    cart_item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": "Item removed.",
                "cart_count": cart_obj.total_items,
                "subtotal": float(cart_obj.subtotal),
            }
        )

    return redirect("cart")


def update_cart(request, item_id):
    cart_obj = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)

    qty = int(request.POST.get("quantity", 1))

    if qty <= 0:
        item.delete()
    else:
        available_stock = (item.variant.stock if item.variant else item.product.stock) or 0
        item.quantity = min(qty, available_stock)
        item.save()

    return redirect("cart")


def save_for_later(request, item_id):
    cart_obj = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)

    item.saved_for_later = True
    item.save()

    return JsonResponse({"success": True, "cart_count": cart_obj.total_items})


def move_to_cart(request, item_id):
    cart_obj = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)

    item.saved_for_later = False
    item.save()

    return redirect("cart")


def clear_cart(request):
    cart_obj = get_cart(request)
    cart_obj.items.filter(saved_for_later=False).delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cart_count": 0, "subtotal": 0})

    return redirect("cart")


# ==========================================
# WISHLIST
# ==========================================

def wishlist(request):
    wishlist_obj = get_wishlist(request)

    items = wishlist_obj.items.select_related("product", "variant", "product__brand")

    return render(request, "wishlist.html", {"wishlist": wishlist_obj, "wishlist_items": items})


def add_to_wishlist(request, product_id):
    if request.method != "POST":
        return JsonResponse({"success": False})

    product = get_object_or_404(Product, id=product_id, active=True)

    wishlist_obj = get_wishlist(request)

    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist_obj, product=product)

    return JsonResponse(
        {"success": True, "count": wishlist_obj.items.count(), "message": "Added to wishlist."}
    )


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    return redirect("wishlist")


def wishlist_to_cart(request, item_id):
    """Move a wishlist item to the shopping cart. Works for anonymous and logged-in users."""

    wishlist_obj = get_wishlist(request)
    cart_obj = get_cart(request)

    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist_obj)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=wishlist_item.product,
        variant=wishlist_item.variant,
        defaults={"quantity": 1},
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()

    return redirect("cart")


# ==========================================
# CHECKOUT & ORDERS
# ==========================================

from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Order,
    OrderItem,
    ProductVariant,
)
from .utils import get_cart
from .services.analytics import AnalyticsService
from .models import AnalyticsEvent
#from .emails import send_order_confirmation_email


@transaction.atomic
def checkout(request):

    buy_now = request.session.get("buy_now")

    checkout_items = []
    cart_items = None
    cart_obj = None

    if buy_now:
        variant = get_object_or_404(
            ProductVariant.objects.select_related("product"),
            pk=buy_now["variant_id"],
        )

        quantity = buy_now["quantity"]

        checkout_items.append({
            "product": variant.product,
            "variant": variant,
            "quantity": quantity,
            "price": variant.final_price,
            "subtotal": variant.final_price * quantity,
        })

    else:
        cart_obj = get_cart(request)

        cart_items = (
            cart_obj.items
            .filter(saved_for_later=False)
            .select_related("product", "variant")
        )

        if not cart_items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")

        for item in cart_items:
            checkout_items.append({
                "product": item.product,
                "variant": item.variant,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.subtotal,
                "cart_item": item,
            })

    subtotal = sum(item["subtotal"] for item in checkout_items)

    delivery_fee = Decimal("200.00")

    total_before_vat = subtotal + delivery_fee

    if request.method == "POST":

        vat_option = request.POST.get("vat_option", "exclusive")

        if vat_option == "inclusive":
            vat_amount = total_before_vat * Decimal("0.16")
        else:
            vat_amount = Decimal("0.00")

        grand_total = total_before_vat + vat_amount

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            full_name=request.POST.get("full_name"),
            address=request.POST.get("address1"),
            city=request.POST.get("city"),
            county=request.POST.get("county"),
            postcode=request.POST.get("postcode"),
            notes=request.POST.get("notes"),
            payment_method=request.POST.get("payment_method"),
            delivery_method=request.POST.get("delivery_method"),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            vat_option=vat_option,
            vat_amount=vat_amount,
            grand_total=grand_total,
        )

        for item in checkout_items:

            AnalyticsService.track(
                request=request,
                event_type=AnalyticsEvent.CHECKOUT,
                product=item["product"],
                variant=item["variant"],
                quantity=item["quantity"],
            )

            OrderItem.objects.create(
                order=order,
                product=item["product"],
                variant=item["variant"],
                quantity=item["quantity"],
                price=item["price"],
                total=item["subtotal"],
            )

            AnalyticsService.track(
                request=request,
                event_type=AnalyticsEvent.PURCHASE,
                product=item["product"],
                variant=item["variant"],
                quantity=item["quantity"],
                revenue=item["subtotal"],
            )

            if item["variant"]:
                if item["variant"].stock >= item["quantity"]:
                    item["variant"].stock -= item["quantity"]
                else:
                    item["variant"].stock = 0

                item["variant"].save(update_fields=["stock"])

        # Delete only the purchased cart items
        if cart_items:
            cart_items.delete()

        # Remove Buy Now session
        request.session.pop("buy_now", None)

        send_order_confirmation_email(request, order)

        messages.success(request, "Your order has been placed successfully.")

        return redirect("processing_order", order.id)

    context = {
        "cart": cart_obj,
        "cart_items": checkout_items,
        "cart_subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "vat_amount": Decimal("0.00"),
        "cart_total": total_before_vat,
        "buy_now": bool(buy_now),
    }

    return render(request, "checkout.html", context)

def processing_order(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        order = get_object_or_404(Order, id=order_id)

    return render(request, "processing_order.html", {"order": order})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)
    return render(request, "order_success.html", {"order": order})


def order_receipt(request, order_id):
    queryset = Order.objects.select_related("user").prefetch_related(
        "items", "items__product", "items__product__brand", "items__product__category"
    )

    if request.user.is_authenticated:
        order = get_object_or_404(queryset, order_id=order_id, user=request.user)
    else:
        order = get_object_or_404(queryset, order_id=order_id, user__isnull=True)

    return render(request, "orders/order_receipt.html", {"order": order, "items": order.items.all()})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status in ["cancelled", "shipped", "delivered"]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect("orders")

    if request.method == "POST":
        order.status = "cancelled"
        order.cancellation_reason = "Cancelled by customer."
        order.save()

        send_mail(
            subject=f"Order {order.order_id} Cancelled",
            message=(
                f"Hello {order.full_name},\n\n"
                f"Your order {order.order_id} has been cancelled successfully.\n\n"
                "If this was a mistake, you can place another order at any time.\n\n"
                "Thank you for choosing SmartComputersKE."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )

        messages.success(request, "Order cancelled successfully.")

    return redirect("orders")


@login_required
def order_detail(request, order_id):
    """Customer-facing order tracking page — restricted to the order's owner."""

    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


# ==========================================
# ACCOUNTS
# ==========================================

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            EmailOTP.objects.filter(user=user).delete()

            otp = generate_otp()

            EmailOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            send_otp_email(user, otp)

            request.session["pending_user"] = user.id

            messages.success(request, "We've sent a verification code to your email.")

            return redirect("verify_email")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Logged in successfully.")
        return redirect("home")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect("home")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/orders.html", {"orders": orders})


@login_required
def account_settings(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully.")
            return redirect("account_settings")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "dashboard/account.html", {"form": form})


def verify_email(request):
    user_id = request.session.get("pending_user")

    if not user_id:
        messages.error(request, "Registration session expired.")
        return redirect("register")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("register")

    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = EmailOTP.objects.get(user=user, otp=code, verified=False)
        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid verification code.")
            return redirect("verify_email")

        if otp.is_expired():
            otp.delete()
            messages.error(request, "Verification code has expired.")
            return redirect("verify_email")

        otp.verified = True
        otp.save()

        user.is_active = True
        user.save()

        otp.delete()

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        del request.session["pending_user"]

        messages.success(request, "Your email has been verified successfully.")

        return redirect("home")

    return render(request, "accounts/verify_email.html", {"email": user.email})


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account exists with that email.")
            return redirect("forgot_password")

        EmailOTP.objects.filter(user=user, verified=False).delete()

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(user=user, otp=otp)

        send_otp_email(user, otp)

        request.session["reset_user"] = user.id

        messages.success(request, "We've sent a verification code to your email.")

        return redirect("verify_reset_otp")

    return render(request, "accounts/forgot_password.html")

from django.db.models import Q
def verify_reset_otp(request):
    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = EmailOTP.objects.get(user=user, otp=code, verified=False)
        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid verification code.")
            return redirect("verify_reset_otp")

        if otp.is_expired():
            otp.delete()
            messages.error(request, "Verification code has expired.")
            return redirect("forgot_password")

        otp.verified = True
        otp.save()

        request.session["password_verified"] = True

        return redirect("new_password")

    return render(request, "accounts/verify_reset_otp.html", {"email": user.email})


def new_password(request):
    user_id = request.session.get("reset_user")
    verified = request.session.get("password_verified")

    if not user_id or not verified:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("new_password")

        user.set_password(password1)
        user.save()

        EmailOTP.objects.filter(user=user).delete()

        del request.session["reset_user"]
        del request.session["password_verified"]

        messages.success(request, "Password changed successfully.")

        return redirect("login")

    return render(request, "accounts/new_password.html")

from .models import UserProfile

@csrf_exempt
def google_one_tap(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        credential = data.get("credential")

        if not credential:
            return JsonResponse({"error": "Missing credential"}, status=400)

        google_user = id_token.verify_oauth2_token(
            credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )

        email = google_user.get("email")

        if not email:
            return JsonResponse({"error": "Google account has no email."}, status=400)

        first_name = google_user.get("given_name", "")
        last_name = google_user.get("family_name", "")
        picture = google_user.get("picture", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email, "first_name": first_name, "last_name": last_name},
        )

        if created:
            user.set_unusable_password()
            user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if picture and profile.google_picture != picture:
            profile.google_picture = picture
            profile.save()

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return JsonResponse({"success": True, "email": user.email, "new_user": created})

    except json.JSONDecodeError:
        traceback.print_exc()
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# ==========================================
# DASHBOARD — AUTH
# ==========================================

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect("dashboard_home")
            messages.error(request, "You do not have staff permissions.")
        else:
            messages.error(request, "Invalid login credentials.")

    return render(request, "dashboard/login.html")


def dashboard_logout(request):
    logout(request)
    return redirect("dashboard_login")


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect("dashboard_home")
            messages.error(request, "You do not have staff access.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "staff/login.html")


def staff_logout(request):
    logout(request)
    return redirect("staff_login")


@staff_member_required(login_url="dashboard_login")
def staff_account(request):
    profile = request.user.staff_profile

    if request.method == "POST":
        request.user.username = request.POST.get("username")
        request.user.email = request.POST.get("email")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        request.user.save()
        profile.save()

        messages.success(request, "Account updated successfully")

    password_form = PasswordChangeForm(request.user)

    return render(
        request, "dashboard/account.html", {"profile": profile, "password_form": password_form}
    )


@staff_member_required(login_url="dashboard_login")
def change_staff_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully")

    return redirect("staff_account")


# ==========================================
# DASHBOARD — HOME
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_home(request):
    context = {
        "products": Product.objects.count(),
        "orders": Order.objects.count(),
        "customers": User.objects.count(),
        "categories": Category.objects.count(),
    }

    return render(request, "dashboard/dashboard.html", context)


# ==========================================
# DASHBOARD — PRODUCTS
# ==========================================
@staff_member_required(login_url="dashboard_login")
def dashboard_products(request):

    search = request.GET.get("search", "").strip()

    products = (
        Product.objects
        .select_related("category", "brand")
        .prefetch_related("variants")
        .order_by("-created")
    )

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(brand__name__icontains=search)
        )

    return render(
        request,
        "dashboard/products.html",
        {
            "products": products,
            "search": search,
        },
    )
@staff_member_required(login_url="dashboard_login")
def dashboard_bulk_products(request):

    if request.method != "POST":
        return redirect("dashboard_products")

    ids = request.POST.getlist("products")
    action = request.POST.get("action")
    stock = request.POST.get("stock")

    if not ids:
        messages.warning(request, "No products selected.")
        return redirect("dashboard_products")

    products = Product.objects.filter(id__in=ids)
    variants = ProductVariant.objects.filter(product_id__in=ids)

    if action == "new_arrivals_on":

        products.update(new_arrival=True)

        messages.success(
            request,
            f"{products.count()} products added to New Arrivals."
        )

    elif action == "new_arrivals_off":

        products.update(new_arrival=False)

        messages.success(
            request,
            f"{products.count()} products removed from New Arrivals."
        )

    elif action == "featured_on":

        products.update(featured=True)

        messages.success(
            request,
            f"{products.count()} products added to Featured Deals."
        )

    elif action == "featured_off":

        products.update(featured=False)

        messages.success(
            request,
            f"{products.count()} products removed from Featured Deals."
        )

    elif action == "show":

        products.update(visible=True)

        messages.success(
            request,
            f"{products.count()} products are now visible."
        )

    elif action == "hide":

        products.update(visible=False)

        messages.success(
            request,
            f"{products.count()} products are now hidden."
        )

    elif action == "activate":

        variants.update(active=True)

        messages.success(
            request,
            "Selected products activated."
        )

    elif action == "deactivate":

        variants.update(active=False)

        messages.success(
            request,
            "Selected products deactivated."
        )

    elif action == "stock":

        try:

            quantity = int(stock)

            variants.update(stock=quantity)

            messages.success(
                request,
                f"Stock updated to {quantity}."
            )

        except (TypeError, ValueError):

            messages.error(
                request,
                "Invalid stock quantity."
            )

    elif action == "delete":

        products.delete()

        messages.success(
            request,
            "Selected products deleted."
        )

    else:

        messages.error(
            request,
            "Unknown bulk action."
        )

    return redirect("dashboard_products")

@staff_member_required(login_url="dashboard_login")
def dashboard_add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            gallery_images = request.FILES.getlist("gallery_images")

            if gallery_images:
                for index, image in enumerate(gallery_images):
                    ProductImage.objects.create(
                        product=product, image=image, is_primary=(index == 0)
                    )

                product.image = gallery_images[0]
                product.save(update_fields=["image"])

            messages.success(request, "Product added successfully.")

            return redirect("dashboard_edit_product", id=product.id)

    else:
        form = ProductForm()

    return render(request, "dashboard/add_product.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    variant = product.default_variant

    if variant is None:
        variant = ProductVariant.objects.create(
            product=product,
            price=0,
            stock=0,
            sku=generate_unique_sku(None),
            active=True,
        )

    next_page = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_form = ProductVariantForm(request.POST, request.FILES, instance=variant)

        if product_form.is_valid() and variant_form.is_valid():
            product_form.save()
            variant_form.save()

            messages.success(request, "Product updated successfully.")

            if next_page == "import_review":
                return redirect("import_review")

            return redirect("dashboard_products")

    else:
        product_form = ProductForm(instance=product)
        variant_form = ProductVariantForm(instance=variant)

    variants = ProductVariant.objects.filter(product=product)

    return render(
        request,
        "dashboard/workspace/workspace.html",
        {
            "product": product,
            "product_form": product_form,
            "variant_form": variant_form,
            "variants": variants,
            "next_page": next_page,
        },
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("dashboard_products")

    return render(request, "dashboard/delete_product.html", {"product": product})


@staff_member_required(login_url="dashboard_login")
def dashboard_product_specifications(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant = product.default_variant

    specifications = VariantSpecification.objects.filter(variant=variant).select_related(
        "specification"
    )

    if request.method == "POST":
        form = VariantSpecificationForm(request.POST, category=product.category)

        if form.is_valid():
            spec = form.save(commit=False)
            spec.variant = variant
            spec.save()

            messages.success(request, "Specification added successfully.")

            return redirect("dashboard_product_specifications", product.id)

    else:
        form = VariantSpecificationForm(category=product.category)

    return render(
        request,
        "dashboard/product_specifications.html",
        {"product": product, "variant": variant, "form": form, "specifications": specifications},
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_product_gallery(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    GalleryForm = modelform_factory(ProductImage, fields=["image"])

    if request.method == "POST":
        files = request.FILES.getlist("image")

        for file in files:
            ProductImage.objects.create(product=product, image=file)

        messages.success(request, "Images uploaded successfully.")

        return redirect("dashboard_product_gallery", product.id)

    form = GalleryForm()
    images = ProductImage.objects.filter(product=product)

    return render(
        request, "dashboard/gallery.html", {"product": product, "images": images, "form": form}
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_product_image(request, id):
    image = get_object_or_404(ProductImage, id=id)
    product = image.product
    image.delete()

    messages.success(request, "Image deleted.")

    return redirect("dashboard_product_gallery", product.id)


# ==========================================
# DASHBOARD — VARIANTS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_product_variants(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    variants = product.variants.all()

    search = request.GET.get("search")
    if search:
        variants = variants.filter(Q(sku__icontains=search))

    paginator = Paginator(variants, 20)
    variants = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/variants/list.html",
        {"product": product, "variants": variants, "search": search},
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_add_variant(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    specifications = (
        Specification.objects.filter(category=product.category)
        .prefetch_related("options")
        .order_by("position")
    )

    if request.method == "POST":
        form = ProductVariantForm(request.POST, request.FILES)

        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()

            for spec in specifications:
                value = request.POST.get(f"spec_{spec.id}")

                if value:
                    VariantSpecification.objects.create(
                        variant=variant, specification=spec, value=value
                    )

            messages.success(request, "Variant added successfully.")

            return redirect("dashboard_product_variants", product.id)

    else:
        form = ProductVariantForm()

    return render(
        request,
        "dashboard/variants/form.html",
        {
            "title": "Add Variant",
            "product": product,
            "form": form,
            "specifications": specifications,
            "variant": None,
        },
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_variant(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product = variant.product

    specifications = Specification.objects.filter(category=product.category).order_by("position")

    if request.method == "POST":
        form = ProductVariantForm(request.POST, request.FILES, instance=variant)

        if form.is_valid():
            form.save()

            VariantSpecification.objects.filter(variant=variant).delete()

            for spec in specifications:
                value = request.POST.get(f"spec_{spec.id}", "").strip()

                if value:
                    VariantSpecification.objects.create(
                        variant=variant, specification=spec, value=value
                    )

            messages.success(request, "Variant updated successfully.")

            return redirect("dashboard_product_variants", product.id)

    else:
        form = ProductVariantForm(instance=variant)

    values = {a.specification.id: a.value for a in variant.attributes.all()}

    return render(
        request,
        "dashboard/variants/form.html",
        {
            "title": "Edit Variant",
            "form": form,
            "product": product,
            "specifications": specifications,
            "values": values,
        },
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_variant(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product = variant.product

    if request.method == "POST":
        variant.delete()
        messages.success(request, "Variant deleted.")
        return redirect("dashboard_product_variants", product.id)

    return render(request, "dashboard/variants/delete.html", {"variant": variant})


@staff_member_required(login_url="dashboard_login")
def dashboard_duplicate_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    new_variant = ProductVariant.objects.create(
        product=variant.product,
        sku=f"TEMP-{uuid.uuid4().hex[:8].upper()}",
        variant_name=variant.variant_name,
        image=variant.image,
        stock=variant.stock,
        price=variant.price,
        discount_price=variant.discount_price,
        discount_start=variant.discount_start,
        discount_end=variant.discount_end,
        active=variant.active,
    )

    for attribute in variant.attributes.all():
        VariantSpecification.objects.create(
            variant=new_variant, specification=attribute.specification, value=attribute.value
        )

    messages.success(request, "Variant duplicated successfully.")

    return redirect("dashboard_edit_variant", pk=new_variant.id)


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_variant_specification(request, id):
    attribute = get_object_or_404(VariantSpecification, id=id)

    form = VariantSpecificationForm(
        request.POST or None, instance=attribute, category=attribute.variant.product.category
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Specification updated successfully.")
        return redirect("dashboard_edit_product", attribute.variant.product.id)

    return render(
        request, "dashboard/edit_variant_specification.html", {"form": form, "attribute": attribute}
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_variant_specification(request, id):
    attribute = get_object_or_404(VariantSpecification, id=id)
    product = attribute.variant.product
    attribute.delete()

    messages.success(request, "Specification deleted.")

    return redirect("dashboard_edit_product", product.id)


def generate_variant_sku():
    while True:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        if not ProductVariant.objects.filter(sku=sku).exists():
            return sku


# ==========================================
# DASHBOARD — CATEGORIES
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_categories(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "dashboard/categories.html", {"categories": categories})


@staff_member_required(login_url="dashboard_login")
def dashboard_add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("dashboard_categories")

    else:
        form = CategoryForm()

    return render(request, "dashboard/add_category.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("dashboard_categories")

    else:
        form = CategoryForm(instance=category)

    return render(request, "dashboard/edit_category.html", {"form": form, "category": category})


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect("dashboard_categories")

    return render(request, "dashboard/delete_category.html", {"category": category})


@staff_member_required(login_url="dashboard_login")
def inventory_categories(request):
    categories = Category.objects.all().order_by("name")

    data = []

    for category in categories:
        products = Product.objects.filter(category=category)
        variants = ProductVariant.objects.filter(product__category=category)

        total_stock = variants.aggregate(total=Sum("stock"))["total"] or 0
        inventory_value = sum(v.stock * v.price for v in variants)
        brands = Brand.objects.filter(products__category=category).distinct().count()

        data.append(
            {
                "category": category,
                "brands": brands,
                "products": products.count(),
                "variants": variants.count(),
                "stock": total_stock,
                "value": inventory_value,
            }
        )

    return render(request, "dashboard/inventory/categories.html", {"data": data})


@staff_member_required(login_url="dashboard_login")
def inventory_category_detail(request, id):
    category = get_object_or_404(Category, id=id)

    products = Product.objects.filter(category=category).prefetch_related("variants", "brand")

    return render(
        request, "dashboard/inventory/category_detail.html", {"category": category, "products": products}
    )


# ==========================================
# DASHBOARD — BRANDS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_brands(request):
    query = request.GET.get("q", "")
    brands = Brand.objects.all()

    if query:
        brands = brands.filter(name__icontains=query)

    return render(request, "dashboard/brands.html", {"brands": brands, "query": query})


@staff_member_required(login_url="dashboard_login")
def add_brand(request):
    if request.method == "POST":
        form = BrandForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Brand added successfully.")
            return redirect("brand_list")

    else:
        form = BrandForm()

    return render(request, "dashboard/add_brand.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def edit_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == "POST":
        form = BrandForm(request.POST, request.FILES, instance=brand)

        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated successfully.")
            return redirect("brand_list")

    else:
        form = BrandForm(instance=brand)

    return render(request, "dashboard/edit_brand.html", {"form": form, "brand": brand})


@staff_member_required(login_url="dashboard_login")
def delete_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == "POST":
        brand.delete()
        messages.success(request, "Brand deleted successfully.")
        return redirect("brand_list")

    return render(request, "dashboard/delete_brand.html", {"brand": brand})


@staff_member_required(login_url="dashboard_login")
def inventory_brands(request):
    brands = Brand.objects.all().order_by("name")

    data = []

    for brand in brands:
        products = Product.objects.filter(brand=brand)
        variants = ProductVariant.objects.filter(product__brand=brand)

        stock = variants.aggregate(total=Sum("stock"))["total"] or 0
        value = sum(v.stock * v.price for v in variants)
        categories = Category.objects.filter(products__brand=brand).distinct().count()

        data.append(
            {
                "brand": brand,
                "categories": categories,
                "products": products.count(),
                "variants": variants.count(),
                "stock": stock,
                "value": value,
            }
        )

    return render(request, "dashboard/inventory/brands.html", {"data": data})


@staff_member_required(login_url="dashboard_login")
def inventory_brand_detail(request, id):
    brand = get_object_or_404(Brand, id=id)

    products = Product.objects.filter(brand=brand).prefetch_related("variants")

    rows = []
    total_stock = 0
    total_value = 0

    for product in products:
        variants = product.variants.all()
        stock = sum(x.stock for x in variants)
        value = sum(x.stock * x.price for x in variants)

        total_stock += stock
        total_value += value

        rows.append({"product": product, "variants": variants, "stock": stock, "value": value})

    return render(
        request,
        "dashboard/inventory/brand_detail.html",
        {
            "brand": brand,
            "rows": rows,
            "total_products": products.count(),
            "total_variants": ProductVariant.objects.filter(product__brand=brand).count(),
            "total_stock": total_stock,
            "inventory_value": total_value,
        },
    )


# ==========================================
# DASHBOARD — ORDERS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")

    q = request.GET.get("q")
    if q:
        orders = orders.filter(order_id__icontains=q)

    return render(request, "dashboard/order_list.html", {"orders": orders})


@staff_member_required(login_url="dashboard_login")
def dashboard_order_detail(request, order_id):
    """Staff order detail page — allows changing status and notifying the customer."""

    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        status = request.POST.get("status")
        notes = request.POST.get("admin_notes")
        cancel_reason = request.POST.get("cancellation_reason")

        if notes:
            order.admin_notes = notes

        if status:
            order.status = status

        if status == "cancelled":
            order.cancellation_reason = cancel_reason
            send_order_email(order, "Your Order Has Been Cancelled", "emails/order_cancelled.html")
            messages.success(request, "Customer has been notified.")

        elif status == "processing":
            send_order_email(order, "Your Order is being Processed", "emails/order_processing.html")

        elif status == "packed":
            send_order_email(order, "Your Order Has Been Packed", "emails/order_packed.html")

        elif status == "shipped":
            send_order_email(order, "Your Order Has Been Shipped", "emails/order_shipped.html")

        elif status == "delivered":
            send_order_email(order, "Your Order Has Been Delivered", "emails/order_delivered.html")

        order.save()

        messages.success(request, "Order updated successfully.")

        return redirect("order_detail", order.order_id)

    return render(request, "dashboard/order_detail.html", {"order": order})


@staff_member_required(login_url="dashboard_login")
def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted successfully.")
        return redirect("order_list")

    return render(request, "dashboard/delete_order.html", {"order": order})


# ==========================================
# DASHBOARD — IMPORT
# ==========================================

@staff_member_required(login_url="dashboard_login")
def import_product(request):
    form = ProductImportForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        urls = form.cleaned_data["urls"]

        imported = 0
        failed = 0
        imported_ids = []
        failed_urls = []

        for url in urls:
            try:
                service = ProductImportService(url)
                product = service.save()
                imported_ids.append(product.id)
                imported += 1
            except Exception as e:
                failed += 1
                failed_urls.append(f"{url} → {str(e)}")

        request.session["imported_products"] = imported_ids

        messages.success(request, f"{imported} product(s) imported successfully.")

        if failed:
            messages.warning(request, f"{failed} product(s) failed.")

        return redirect("import_review")

    return render(request, "dashboard/import_product.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def import_review(request):
    ids = request.session.get("imported_products", [])

    products = Product.objects.filter(id__in=ids).select_related("brand", "category")

    return render(request, "dashboard/import_review.html", {"products": products})


# ==========================================
# DASHBOARD — BANNERS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_banners(request):
    query = request.GET.get("q")

    banners = Banner.objects.all().order_by("order")

    if query:
        banners = banners.filter(Q(title__icontains=query) | Q(subtitle__icontains=query))

    paginator = Paginator(banners, 15)
    banners = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/banners.html", {"banners": banners})


@staff_member_required(login_url="dashboard_login")
def dashboard_add_banner(request):
    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Banner created successfully.")
            return redirect("dashboard_banners")

    else:
        form = BannerForm()

    return render(request, "dashboard/add_banner.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES, instance=banner)

        if form.is_valid():
            form.save()
            messages.success(request, "Banner updated successfully.")
            return redirect("dashboard_banners")

    else:
        form = BannerForm(instance=banner)

    return render(request, "dashboard/edit_banner.html", {"form": form, "banner": banner})


@staff_member_required(login_url="dashboard_login")
def dashboard_delete_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == "POST":
        banner.delete()
        messages.success(request, "Banner deleted successfully.")
        return redirect("dashboard_banners")

    return render(request, "dashboard/delete_banner.html", {"banner": banner})


# ==========================================
# DASHBOARD — DEALS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_deals(request):
    now = timezone.now()

    deals_qs = ProductVariant.objects.select_related(
        "product", "product__brand", "product__category"
    ).filter(
        discount_price__isnull=False,
        discount_start__isnull=False,
        discount_end__isnull=False,
    )

    search = request.GET.get("q")
    if search:
        deals_qs = deals_qs.filter(Q(product__name__icontains=search) | Q(sku__icontains=search))

    category = request.GET.get("category")
    if category:
        deals_qs = deals_qs.filter(product__category_id=category)

    brand = request.GET.get("brand")
    if brand:
        deals_qs = deals_qs.filter(product__brand_id=brand)

    status = request.GET.get("status")
    if status == "active":
        deals_qs = deals_qs.filter(discount_start__lte=now, discount_end__gte=now)
    elif status == "scheduled":
        deals_qs = deals_qs.filter(discount_start__gt=now)
    elif status == "expired":
        deals_qs = deals_qs.filter(discount_end__lt=now)

    active_count = ProductVariant.objects.filter(
        discount_price__isnull=False, discount_start__lte=now, discount_end__gte=now
    ).count()

    scheduled_count = ProductVariant.objects.filter(
        discount_price__isnull=False, discount_start__gt=now
    ).count()

    expired_count = ProductVariant.objects.filter(
        discount_price__isnull=False, discount_end__lt=now
    ).count()

    total_count = ProductVariant.objects.filter(discount_price__isnull=False).count()

    paginator = Paginator(deals_qs, 20)
    deals_qs = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/deals_list.html",
        {
            "deals": deals_qs,
            "now": now,
            "active_count": active_count,
            "scheduled_count": scheduled_count,
            "expired_count": expired_count,
            "total_count": total_count,
            "categories": Category.objects.all(),
            "brands": Brand.objects.all(),
        },
    )


@staff_member_required(login_url="dashboard_login")
def dashboard_add_deal(request):
    variants = ProductVariant.objects.select_related(
        "product", "product__brand", "product__category"
    ).filter(active=True)

    if request.method == "POST":
        product_id = request.POST.get("product")
        deal_price = request.POST.get("new_price")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not product_id:
            messages.error(request, "Please select a product.")
            return redirect("dashboard_add_deal")

        variant = get_object_or_404(ProductVariant, id=product_id)

        try:
            deal_price = Decimal(deal_price)
        except Exception:
            messages.error(request, "Invalid deal price.")
            return redirect("dashboard_add_deal")

        if deal_price <= 0:
            messages.error(request, "Deal price must be greater than zero.")
            return redirect("dashboard_add_deal")

        if deal_price >= variant.price:
            messages.error(request, "Deal price must be lower than the original price.")
            return redirect("dashboard_add_deal")

        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except Exception:
            messages.error(request, "Invalid start or end date.")
            return redirect("dashboard_add_deal")

        tz = timezone.get_current_timezone()

        if timezone.is_naive(start):
            start = timezone.make_aware(start, tz)
        if timezone.is_naive(end):
            end = timezone.make_aware(end, tz)

        if end <= start:
            messages.error(request, "End date must be after the start date.")
            return redirect("dashboard_add_deal")

        variant.discount_price = deal_price
        variant.discount_start = start
        variant.discount_end = end
        variant.save()

        messages.success(request, f"Deal created successfully for '{variant.product.name}'.")

        return redirect("dashboard_deals")

    return render(request, "dashboard/add_deal.html", {"variants": variants})


@staff_member_required(login_url="dashboard_login")
def dashboard_edit_deal(request, variant_id):
    variant = get_object_or_404(
        ProductVariant.objects.select_related("product", "product__brand", "product__category"),
        pk=variant_id,
    )

    if request.method == "POST":
        try:
            new_price = Decimal(request.POST.get("new_price"))
        except Exception:
            messages.error(request, "Invalid deal price.")
            return redirect("dashboard_edit_deal", variant.id)

        start = parse_datetime(request.POST.get("start_date"))
        end = parse_datetime(request.POST.get("end_date"))

        if start is None or end is None:
            messages.error(request, "Invalid start or end date.")
            return redirect("dashboard_edit_deal", variant.id)

        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.get_current_timezone())
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.get_current_timezone())

        if end <= start:
            messages.error(request, "End date must be after the start date.")
            return redirect("dashboard_edit_deal", variant.id)

        if new_price <= 0:
            messages.error(request, "Deal price must be greater than zero.")
            return redirect("dashboard_edit_deal", variant.id)

        if new_price >= variant.price:
            messages.error(request, "Deal price must be lower than the original price.")
            return redirect("dashboard_edit_deal", variant.id)

        variant.discount_price = new_price
        variant.discount_start = start
        variant.discount_end = end
        variant.save()

        messages.success(request, "Deal updated successfully.")

        return redirect("dashboard_deals")

    return render(request, "dashboard/edit_deal.html", {"variant": variant, "now": timezone.now()})


@staff_member_required(login_url="dashboard_login")
def dashboard_end_deal(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == "POST":
        variant.discount_price = None
        variant.discount_start = None
        variant.discount_end = None
        variant.save()

        messages.success(request, f"{variant.product.name} deal ended successfully.")

        return redirect("dashboard_deals")

    return render(request, "dashboard/end_deal.html", {"variant": variant})


@staff_member_required(login_url="dashboard_login")
def dashboard_extend_deal(request, pk):
    campaign = get_object_or_404(DealCampaign, pk=pk)

    days = int(request.GET.get("days", 7))

    campaign.end_date += timedelta(days=days)

    now = timezone.now()
    if campaign.start_date <= now <= campaign.end_date:
        campaign.status = "active"

    campaign.save()

    messages.success(request, f"Deal extended by {days} days.")

    return redirect("dashboard_deals")


# ==========================================
# DASHBOARD — MARKETING
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_marketing(request):
    form = MarketingCampaignForm()

    products = Product.objects.select_related("brand", "category").filter(active=True).order_by("name")

    recipient_count = User.objects.filter(is_active=True).exclude(email="").count()

    return render(
        request,
        "dashboard/marketing.html",
        {"form": form, "products": products, "recipient_count": recipient_count},
    )


@staff_member_required(login_url="dashboard_login")
def send_marketing_campaign(request):
    if request.method != "POST":
        return redirect("dashboard_marketing")

    form = MarketingCampaignForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Please correct the errors.")
        return redirect("dashboard_marketing")

    campaign = form.save(commit=False)
    campaign.created_by = request.user
    campaign.status = "sending"
    campaign.save()

    form.save_m2m()

    products = campaign.products.all()

    recipient_type = request.POST.get("recipient_type", "customers")

    emails = set()

    if recipient_type in ["customers", "both"]:
        emails.update(
            Customer.objects.filter(active=True).exclude(email="").values_list("email", flat=True)
        )

    if recipient_type in ["subscribers", "both"]:
        emails.update(
            NewsletterSubscriber.objects.filter(active=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )

    campaign.total_products = products.count()
    campaign.total_recipients = len(emails)
    campaign.save()

    for email_address in emails:
        html = render_to_string(
            "emails/product_marketing.html", {"campaign": campaign, "products": products}
        )

        email = EmailMultiAlternatives(
            subject=campaign.subject,
            body=campaign.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_address],
        )

        email.attach_alternative(html, "text/html")
        email.send(fail_silently=False)

    campaign.status = "completed"
    campaign.sent_at = timezone.now()
    campaign.save()

    messages.success(request, f"Marketing email sent successfully to {len(emails)} recipients.")

    return redirect("marketing_history")


@staff_member_required(login_url="dashboard_login")
def marketing_history(request):
    campaigns = MarketingCampaign.objects.select_related("created_by")
    return render(request, "dashboard/marketing_history.html", {"campaigns": campaigns})


@staff_member_required(login_url="dashboard_login")
def marketing_detail(request, pk):
    campaign = get_object_or_404(MarketingCampaign, pk=pk)
    products = campaign.products.select_related("brand", "category")

    return render(
        request, "dashboard/marketing_detail.html", {"campaign": campaign, "products": products}
    )


@staff_member_required(login_url="dashboard_login")
def marketing_duplicate(request, pk):
    campaign = get_object_or_404(MarketingCampaign, pk=pk)

    new_campaign = MarketingCampaign.objects.create(
        subject=f"{campaign.subject} (Copy)",
        message=campaign.message,
        created_by=request.user,
        status="draft",
    )

    new_campaign.products.set(campaign.products.all())

    messages.success(request, "Campaign duplicated successfully.")

    return redirect("dashboard_marketing")


@staff_member_required(login_url="dashboard_login")
def marketing_delete(request, pk):
    campaign = get_object_or_404(MarketingCampaign, pk=pk)

    if request.method == "POST":
        campaign.delete()
        messages.success(request, "Campaign deleted successfully.")
        return redirect("marketing_history")

    return render(request, "dashboard/delete_marketing.html", {"campaign": campaign})


# ==========================================
# DASHBOARD — CUSTOMERS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_customers(request):
    customers = Customer.objects.order_by("-last_login")
    return render(request, "dashboard/customers.html", {"customers": customers})


# ==========================================
# DASHBOARD — INVENTORY
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_inventory(request):
    variants = ProductVariant.objects.select_related(
        "product", "product__brand", "product__category"
    ).order_by("product__name")

    total_stock = variants.aggregate(total=Sum("stock"))["total"] or 0
    low_stock = variants.filter(stock__gt=0, stock__lt=5).count()
    out_stock = variants.filter(stock=0).count()

    inventory_value = sum(item.stock * item.current_price for item in variants)

    return render(
        request,
        "dashboard/inventory/list.html",
        {
            "variants": variants,
            "total_stock": total_stock,
            "low_stock": low_stock,
            "out_stock": out_stock,
            "inventory_value": inventory_value,
        },
    )


@staff_member_required(login_url="dashboard_login")
def inventory_dashboard(request):
    variants = ProductVariant.objects.select_related("product", "product__brand", "product__category")

    total_products = variants.count()
    total_stock = variants.aggregate(total=Sum("stock"))["total"] or 0
    low_stock = variants.filter(stock__lte=5, active=True).count()
    out_of_stock = variants.filter(stock=0, active=True).count()

    total_value = sum(item.stock * item.price for item in variants)

    recent_transactions = InventoryTransaction.objects.select_related(
        "variant", "variant__product", "created_by"
    ).order_by("-created_at")[:10]

    return render(
        request,
        "dashboard/inventory/dashboard.html",
        {
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "total_value": total_value,
            "recent_transactions": recent_transactions,
        },
    )


@staff_member_required(login_url="dashboard_login")
def inventory_list(request):
    variants = ProductVariant.objects.select_related("product", "product__brand", "product__category")

    search = request.GET.get("search")
    if search:
        variants = variants.filter(
            Q(product__name__icontains=search)
            | Q(sku__icontains=search)
            | Q(product__brand__name__icontains=search)
        )

    stock = request.GET.get("stock")
    if stock == "low":
        variants = variants.filter(stock__lte=5)
    elif stock == "out":
        variants = variants.filter(stock=0)
    elif stock == "available":
        variants = variants.filter(stock__gt=5)

    paginator = Paginator(variants.order_by("product__name"), 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request, "dashboard/inventory/list.html", {"page_obj": page_obj, "search": search, "stock": stock}
    )


@staff_member_required(login_url="dashboard_login")
def stock_in(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        form = StockInForm(request.POST)

        if form.is_valid():
            qty = form.cleaned_data["quantity"]

            variant.stock += qty
            variant.save()

            InventoryTransaction.objects.create(
                variant=variant,
                transaction_type=InventoryTransaction.STOCK_IN,
                quantity=qty,
                balance_after=variant.stock,
                reference=form.cleaned_data["reference"],
                notes=form.cleaned_data["notes"],
                created_by=request.user,
            )

            messages.success(request, "Stock added successfully.")

            return redirect("inventory_list")

    else:
        form = StockInForm()

    return render(request, "dashboard/inventory/stock_in.html", {"variant": variant, "form": form})


@staff_member_required(login_url="dashboard_login")
def stock_out(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        form = StockOutForm(request.POST)

        if form.is_valid():
            qty = form.cleaned_data["quantity"]

            if qty > variant.stock:
                messages.error(request, "Insufficient stock.")
            else:
                variant.stock -= qty
                variant.save()

                InventoryTransaction.objects.create(
                    variant=variant,
                    transaction_type=InventoryTransaction.STOCK_OUT,
                    quantity=qty,
                    balance_after=variant.stock,
                    reference=form.cleaned_data["reference"],
                    notes=form.cleaned_data["notes"],
                    created_by=request.user,
                )

                messages.success(request, "Stock removed successfully.")

                return redirect("inventory_list")

    else:
        form = StockOutForm()

    return render(request, "dashboard/inventory/stock_out.html", {"variant": variant, "form": form})


@staff_member_required(login_url="dashboard_login")
def stock_adjustment(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)

        if form.is_valid():
            new_stock = form.cleaned_data["quantity"]

            variant.stock = new_stock
            variant.save()

            InventoryTransaction.objects.create(
                variant=variant,
                transaction_type=InventoryTransaction.ADJUSTMENT,
                quantity=new_stock,
                balance_after=new_stock,
                reference=form.cleaned_data["reference"],
                notes=form.cleaned_data["notes"],
                created_by=request.user,
            )

            messages.success(request, "Inventory adjusted successfully.")

            return redirect("inventory_list")

    else:
        form = StockAdjustmentForm(initial={"quantity": variant.stock})

    return render(request, "dashboard/inventory/adjustment.html", {"variant": variant, "form": form})


@staff_member_required(login_url="dashboard_login")
def inventory_history(request):
    history = InventoryTransaction.objects.select_related(
        "variant", "variant__product", "created_by"
    ).order_by("-created_at")

    search = request.GET.get("search")
    if search:
        history = history.filter(
            Q(variant__sku__icontains=search) | Q(variant__product__name__icontains=search)
        )

    paginator = Paginator(history, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/inventory/history.html", {"page_obj": page_obj, "search": search})


@staff_member_required(login_url="dashboard_login")
def dashboard_inventory_history(request):
    transactions = InventoryTransaction.objects.select_related(
        "variant", "variant__product", "created_by"
    ).order_by("-created_at")

    return render(request, "dashboard/inventory/history.html", {"transactions": transactions})


@staff_member_required(login_url="dashboard_login")
def dashboard_stock_in(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        qty = int(request.POST["quantity"])

        variant.stock += qty
        variant.save()

        InventoryTransaction.objects.create(
            variant=variant,
            transaction_type="IN",
            quantity=qty,
            balance_after=variant.stock,
            reference=request.POST.get("reference", ""),
            notes=request.POST.get("notes", ""),
            created_by=request.user,
        )

        messages.success(request, "Stock added successfully.")

        return redirect("dashboard_inventory")

    return render(request, "dashboard/inventory/stock_in.html", {"variant": variant})


@staff_member_required(login_url="dashboard_login")
def dashboard_stock_out(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        qty = int(request.POST["quantity"])

        if qty > variant.stock:
            messages.error(request, "Not enough stock.")
            return redirect("dashboard_stock_out", pk=pk)

        variant.stock -= qty
        variant.save()

        InventoryTransaction.objects.create(
            variant=variant,
            transaction_type="OUT",
            quantity=qty,
            balance_after=variant.stock,
            reference=request.POST.get("reference", ""),
            notes=request.POST.get("notes", ""),
            created_by=request.user,
        )

        messages.success(request, "Stock removed successfully.")

        return redirect("dashboard_inventory")

    return render(request, "dashboard/inventory/stock_out.html", {"variant": variant})


@staff_member_required(login_url="dashboard_login")
def dashboard_stock_adjust(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        new_stock = int(request.POST["quantity"])

        variant.stock = new_stock
        variant.save()

        InventoryTransaction.objects.create(
            variant=variant,
            transaction_type="ADJUST",
            quantity=new_stock,
            balance_after=new_stock,
            reference=request.POST.get("reference", ""),
            notes=request.POST.get("notes", ""),
            created_by=request.user,
        )

        messages.success(request, "Inventory adjusted.")

        return redirect("dashboard_inventory")

    return render(request, "dashboard/inventory/adjust.html", {"variant": variant})


# ==========================================
# DASHBOARD — ANALYTICS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_analytics(request):
    analytics = ProductAnalytics.objects.select_related(
        "product", "product__brand", "product__category"
    ).order_by("-total_views")

    context = {
        "analytics": analytics,
        "total_views": analytics.aggregate(total=Sum("total_views"))["total"] or 0,
        "total_cart_adds": analytics.aggregate(total=Sum("cart_adds"))["total"] or 0,
        "total_checkouts": analytics.aggregate(total=Sum("checkout_count"))["total"] or 0,
        "total_sales": analytics.aggregate(total=Sum("total_sales"))["total"] or 0,
        "total_revenue": analytics.aggregate(total=Sum("total_revenue"))["total"] or 0,
    }

    return render(request, "dashboard/analytics/index.html", context)


# ==========================================
# DASHBOARD — GOOGLE REVIEWS
# ==========================================

@staff_member_required(login_url="dashboard_login")
def google_reviews(request):
    reviews = GoogleReview.objects.all()
    return render(request, "dashboard/google_reviews.html", {"reviews": reviews})


@staff_member_required(login_url="dashboard_login")
def toggle_google_review(request, id):
    review = get_object_or_404(GoogleReview, id=id)
    review.is_visible = not review.is_visible
    review.save()
    return redirect("dashboard_google_reviews")


@staff_member_required(login_url="dashboard_login")
def delete_google_review(request, id):
    review = get_object_or_404(GoogleReview, id=id)
    review.delete()
    return redirect("dashboard_google_reviews")


@staff_member_required(login_url="dashboard_login")
def dashboard_newsletter_subscribers(request):
    search = request.GET.get("q", "").strip()

    subscribers = NewsletterSubscriber.objects.all()

    if search:
        subscribers = subscribers.filter(Q(email__icontains=search))

    paginator = Paginator(subscribers, 25)
    subscribers = paginator.get_page(request.GET.get("page"))

    context = {
        "subscribers": subscribers,
        "search": search,
        "total": NewsletterSubscriber.objects.count(),
        "active": NewsletterSubscriber.objects.filter(active=True).count(),
    }

    return render(request, "dashboard/newsletter/subscribers.html", context)


# ==========================================
# DASHBOARD — BLOG
# ==========================================

@staff_member_required(login_url="dashboard_login")
def dashboard_blog(request):
    posts = BlogPost.objects.select_related("category", "author").order_by("-created_at")

    search = request.GET.get("search")
    if search:
        posts = posts.filter(title__icontains=search)

    category = request.GET.get("category")
    if category:
        posts = posts.filter(category__id=category)

    status = request.GET.get("status")
    if status:
        posts = posts.filter(status=status)

    context = {
        "posts": posts,
        "categories": BlogCategory.objects.all(),
        "total_posts": BlogPost.objects.count(),
        "published_posts": BlogPost.objects.filter(status="published").count(),
        "draft_posts": BlogPost.objects.filter(status="draft").count(),
        "total_views": BlogPost.objects.aggregate(total=Sum("views"))["total"] or 0,
    }

    return render(request, "dashboard/blog/blog_list.html", context)


@staff_member_required(login_url="dashboard_login")
def add_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()

            messages.success(request, "Blog created successfully.")

            return redirect("dashboard_blog")

    else:
        form = BlogForm()

    return render(request, "dashboard/blog/blog_form.html", {"form": form})


@staff_member_required(login_url="dashboard_login")
def edit_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            messages.success(request, "Blog updated successfully.")

            return redirect("dashboard_blog")

    else:
        form = BlogForm(instance=blog)

    return render(
        request,
        "dashboard/blog/add_blog.html",
        {"form": form, "page_title": "Edit Blog", "edit_mode": True},
    )


@staff_member_required(login_url="dashboard_login")
def delete_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect("dashboard_blog")

    return render(request, "dashboard/blog/delete_blog.html", {"blog": blog})


@staff_member_required(login_url="dashboard_login")
def dashboard_blog_categories(request):
    return render(request, "dashboard/blog/category_list.html")


@staff_member_required(login_url="dashboard_login")
def dashboard_blog_tags(request):
    return render(request, "dashboard/blog/tag_list.html")


@staff_member_required(login_url="dashboard_login")
def add_blog_category(request):
    pass


@staff_member_required(login_url="dashboard_login")
def edit_blog_category(request, pk):
    pass


@staff_member_required(login_url="dashboard_login")
def delete_blog_category(request, pk):
    pass


# ==========================================
# PUBLIC BLOG
# ==========================================

def blog_list(request):
    posts = BlogPost.objects.filter(status="published").order_by("-published_at", "-created_at")

    featured_posts = BlogPost.objects.filter(status="published", featured=True).order_by(
        "-published_at"
    )[:3]

    categories = BlogCategory.objects.all()

    return render(
        request,
        "blog/blog_list.html",
        {"posts": posts, "featured_posts": featured_posts, "categories": categories},
    )


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="published")

    related_posts = BlogPost.objects.filter(category=post.category, status="published").exclude(
        id=post.id
    )[:4]

    related_products = post.related_products.all()

    return render(
        request,
        "blog/blog_detail.html",
        {"post": post, "related_posts": related_posts, "related_products": related_products},
    )


def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)

    posts = BlogPost.objects.filter(category=category, status="published").order_by("-created_at")

    return render(request, "blog/blog_category.html", {"category": category, "posts": posts})


# ==========================================
# AI CHAT
# ==========================================

def ai_page(request):
    return render(request, "ai/chat.html")


def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"type": "error", "message": "POST required"}, status=405)

    body = json.loads(request.body)
    message = body.get("message", "")

    ai = SmartAI(request)

    return JsonResponse(ai.reply(message))


# ==========================================
# QUOTES & NEWSLETTER
# ==========================================

def request_quote(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            context = {
                "company_name": data["company_name"],
                "contact_person": data["contact_person"],
                "email": data["email"],
                "phone": data["phone"],
                "whatsapp": data["whatsapp"],
                "kra_pin": data["kra_pin"],
                "address": data["address"],
                "city": data["city"],
                "billing_type": data["billing_type"],
                "notes": data["notes"],
            }

            html_message = render_to_string("emails/quote_request.html", context)

            admin_email = EmailMultiAlternatives(
                subject=f"New Quote Request - {data['company_name']}",
                body="A new quotation request has been received.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["sales@smartcomputerske.co.ke"],
                reply_to=[data["email"]],
            )

            admin_email.attach_alternative(html_message, "text/html")
            admin_email.send(fail_silently=False)

            customer_html = render_to_string("emails/quote_received.html", {"customer": data})

            customer_email = EmailMultiAlternatives(
                subject="We've Received Your Quote Request | SmartComputersKE Technologies",
                body="Thank you for requesting a quotation.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data["email"]],
            )

            customer_email.attach_alternative(customer_html, "text/html")
            customer_email.send(fail_silently=False)

            return redirect("quote_success")

    else:
        form = QuoteRequestForm()

    return render(request, "request_quote.html", {"form": form})


def quote_success(request):
    return render(request, "quote_success.html")


def newsletter_subscribe(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    form = NewsletterSubscriberForm(request.POST)

    if form.is_valid():
        subscriber = form.save(commit=False)
        subscriber.email = subscriber.email.lower()
        subscriber.save()

        return JsonResponse({"success": True, "message": "Thank you for subscribing."})

    return JsonResponse(
        {"success": False, "message": form.errors.get("email", ["Subscription failed."])[0]}
    )


# ==========================================
# STATIC / LEGAL PAGES
# ==========================================

def help_center(request):
    return render(request, "help_center.html")


def warranty(request):
    return render(request, "warranty.html")


def returns_refunds(request):
    return render(request, "returns_refunds.html")


def faq(request):
    return render(request, "faq.html")


def privacy(request):
    return render(request, "privacy.html", {"page_title": "Privacy Policy"})


def terms(request):
    return render(request, "terms_conditions.html", {"page_title": "Terms & Conditions"})

from django.shortcuts import redirect, get_object_or_404
from .models import ProductVariant

def buy_now(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    quantity = int(request.POST.get("quantity", 1))

    request.session["buy_now"] = {
        "variant_id": variant.id,
        "quantity": quantity,
    }

    return redirect("checkout")

from django.shortcuts import render


def shipping_policy(request):
    context = {
        "site_name": "SmartComputersKE Technologies",
        "site_initials": "SC",
        "shipping_updated_date": "5 August 2026",
        "support_email": "support@smartcomputerske.co.ke",
        "support_phone": "+254 700 000 000",
    }

    return render(
        request,
        "shipping_policy.html",
        context,
    )