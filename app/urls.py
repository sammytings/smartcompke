from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.Product, name='products'),
    path(

"category/<slug:slug>/",

views.category_products,

name="category_products",

),
path(
        'product/<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),


    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "cart/save/<int:item_id>/",
        views.save_for_later,
        name="save_for_later"
    ),

    path(
        "cart/move/<int:item_id>/",
        views.move_to_cart,
        name="move_to_cart"
    ),

    path(
        "cart/clear/",
        views.clear_cart,
        name="clear_cart"
    ),

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "wishlist/remove/<int:item_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

    path(
        "wishlist/cart/<int:item_id>/",
        views.wishlist_to_cart,
        name="wishlist_to_cart"
    ),
    path(
    "order-success/<int:pk>/",
    views.order_success,
    name="order_success",
),
    path("checkout/", views.checkout, name="checkout"),
    path(
    "deals/",
    views.deals,
    name="deals"
),
    path("compare/", views.compare, name="compare"),
    path("compare/add/<int:product_id>/", views.add_to_compare, name="add_to_compare"),
    path("compare/remove/<int:product_id>/", views.remove_from_compare, name="remove_from_compare"),


    path("login/", views.login_view, name="login"),

    path("register/", views.register_view, name="register"),

    path("logout/", views.logout_view, name="logout"),

    path("profile/", views.profile, name="profile"),
    path("orders/", views.orders_view, name="orders"),
    path(
    "orders/<str:order_id>/",
    views.order_detail,
    name="order_detail",
),

# Dashboard
    path("smartcontrol/", views.dashboard_home, name="dashboard"),
    path("dashboard/login/", views.dashboard_login, name="dashboard_login"),
    path("dashboard/logout/", views.dashboard_logout, name="dashboard_logout"),
# ==========================
# CUSTOM DASHBOARD
# ==========================

    path(
        "smartcontrol/",
        views.dashboard_home,
        name="dashboard_home",
),

    path(
        "dashboard/products/",
        views.dashboard_products,
        name="dashboard_products",
),

    path(
        "dashboard/products/add/",
        views.dashboard_add_product,
        name="dashboard_add_product",
),

    path(
        "dashboard/products/<int:id>/edit/",
        views.dashboard_edit_product,
        name="dashboard_edit_product",
),

    path(
        "dashboard/products/<int:id>/delete/",
        views.dashboard_delete_product,
        name="dashboard_delete_product",
),
# ==========================
# CATEGORY MANAGEMENT
# ==========================

path(
    "dashboard/categories/",
    views.dashboard_categories,
    name="dashboard_categories",
),

path(
    "dashboard/categories/add/",
    views.dashboard_add_category,
    name="dashboard_add_category",
),

path(
    "dashboard/categories/<int:id>/edit/",
    views.dashboard_edit_category,
    name="dashboard_edit_category",
),

path(
    "dashboard/categories/<int:id>/delete/",
    views.dashboard_delete_category,
    name="dashboard_delete_category",
),


    # =====================
    # BRANDS
    # =====================

    path(
    "dashboard/brands/",
    views.dashboard_brands,
    name="dashboard_brands",
),

    path(
        "dashboard/brands/add/",
        views.add_brand,
        name="add_brand"
    ),


    path(
        "dashboard/brands/<int:id>/edit/",
        views.edit_brand,
        name="edit_brand"
    ),
path(
    "dashboard/brands/",
    views.dashboard_brands,
    name="dashboard_brands",
),

    path(
        "dashboard/brands/<int:id>/delete/",
        views.delete_brand,
        name="delete_brand"
    ),
    # =====================
# ORDERS
# =====================


    path(
        "dashboard/orders/",
        views.order_list,
        name="order_list"
),


path(
    "dashboard/orders/<str:order_id>/",
    views.order_detail,
    name="order_detail"
),
path(
    "categories/",
    views.categories_page,
    name="categories_page",
),

path(
    "dashboard/orders/<str:order_id>/delete/",
    views.delete_order,
    name="delete_order"
),
path(
    "dashboard/import-product/",
    views.import_product,
    name="import_product",
),
path("search/", views.product_search, name="product_search"),
path("brands/<slug:slug>/", views.brand_products, name="brand_products"),

    path(
        "dashboard/products/<int:product_id>/variants/",
        views.dashboard_product_variants,
        name="dashboard_product_variants",
    ),

    path(
        "dashboard/products/<int:product_id>/variants/add/",
        views.dashboard_add_variant,
        name="dashboard_add_variant",
    ),

    path(
        "dashboard/variants/<int:pk>/edit/",
        views.dashboard_edit_variant,
        name="dashboard_edit_variant",
    ),

    path(
        "dashboard/variants/<int:pk>/delete/",
        views.dashboard_delete_variant,
        name="dashboard_delete_variant",
    ),
    path(
    "dashboard/variants/<int:variant_id>/duplicate/",
    views.dashboard_duplicate_variant,
    name="dashboard_duplicate_variant",
),
path(
    "verify-email/",
    views.verify_email,
    name="verify_email",
),
path(
    "dashboard/import-review/",
    views.import_review,
    name="import_review",
),
path(
    "dashboard/products/<int:product_id>/specifications/",
    views.dashboard_product_specifications,
    name="dashboard_product_specifications",
),
    path(
        "google-one-tap/",
        views.google_one_tap,
        name="google_one_tap",
    ),
path(
    "dashboard/products/<int:product_id>/gallery/",
    views.dashboard_product_gallery,
    name="dashboard_product_gallery",
),

path(
    "dashboard/gallery/<int:id>/delete/",
    views.dashboard_delete_product_image,
    name="dashboard_delete_product_image",
),
path(
    "dashboard/specifications/<int:id>/edit/",
    views.dashboard_edit_variant_specification,
    name="dashboard_edit_variant_specification",
),

path(
    "dashboard/specifications/<int:id>/delete/",
    views.dashboard_delete_variant_specification,
    name="dashboard_delete_variant_specification",
),
# Banner Dashboard
path(
    "dashboard/banners/",
    views.dashboard_banners,
    name="dashboard_banners",
),

path(
    "dashboard/banners/add/",
    views.dashboard_add_banner,
    name="dashboard_add_banner",
),

path(
    "dashboard/banners/<int:pk>/edit/",
    views.dashboard_edit_banner,
    name="dashboard_edit_banner",
),

path(
    "dashboard/banners/<int:pk>/delete/",
    views.dashboard_delete_banner,
    name="dashboard_delete_banner",
),
# ===========================
# DEALS
# ===========================

path(
    "dashboard/deals/",
    views.dashboard_deals,
    name="dashboard_deals",
),
path(
    "dashboard/<int:variant_id>/end/",
    views.dashboard_end_deal,
    name="dashboard_end_deal",

),
   path(
        "privacy",
        views.privacy,
        name="privacy",
    ),

    path(
        "terms/",
        views.terms,
        name="terms",
    ),
path(
    "dashboard/deals/add/",
    views.dashboard_add_deal,
    name="dashboard_add_deal",
),

path(
    "dashboard/deals/<int:variant_id>/edit/",
    views.dashboard_edit_deal,
    name="dashboard_edit_deal"
),
path(
    "dashboard/deals/<int:pk>/extend/",
    views.dashboard_extend_deal,
    name="dashboard_extend_deal",
),
# ===========================
# MARKETING
# ===========================

path(
    "dashboard/marketing/",
    views.dashboard_marketing,
    name="dashboard_marketing",
),

path(
    "dashboard/marketing/send/",
    views.send_marketing_campaign,
    name="send_marketing_campaign",
),

path(
    "dashboard/marketing/history/",
    views.marketing_history,
    name="marketing_history",
),

path(
    "dashboard/marketing/<int:id>/",
    views.marketing_detail,
    name="marketing_detail",
),
path(
    "dashboard/marketing/<int:pk>/",
    views.marketing_detail,
    name="marketing_detail",
),

path(
    "dashboard/marketing/<int:pk>/duplicate/",
    views.marketing_duplicate,
    name="marketing_duplicate",
),

path(
    "dashboard/marketing/<int:pk>/delete/",
    views.marketing_delete,
    name="marketing_delete",
),
path(
    "dashboard/customers/",
    views.dashboard_customers,
    name="dashboard_customers",
),
path(
    "dashboard/inventory/",
    views.dashboard_inventory,
    name="dashboard_inventory",
),
path(
    "dashboard/inventory/categories/",
    views.inventory_categories,
    name="inventory_categories",
),

path(
    "dashboard/inventory/categories/<int:id>/",
    views.inventory_category_detail,
    name="inventory_category_detail",
),
path(
    "dashboard/inventory/brands/",
    views.inventory_brands,
    name="inventory_brands",
),

path(
    "dashboard/inventory/brands/<int:id>/",
    views.inventory_brand_detail,
    name="inventory_brand_detail",
),
path(
    "dashboard/inventory/",
    views.inventory_dashboard,
    name="inventory_dashboard",
),

path(
    "dashboard/inventory/list/",
    views.inventory_list,
    name="inventory_list",
),

path(
    "dashboard/inventory/stock-in/<int:pk>/",
    views.stock_in,
    name="stock_in",
),

path(
    "dashboard/inventory/stock-out/<int:pk>/",
    views.stock_out,
    name="stock_out",
),

path(
    "dashboard/inventory/adjust/<int:pk>/",
    views.stock_adjustment,
    name="stock_adjustment",
),

path(
    "dashboard/inventory/history/",
    views.inventory_history,
    name="inventory_history",
),
# ==========================
# INVENTORY
# ==========================

path(
    "inventory/",
    views.dashboard_inventory,
    name="dashboard_inventory",
),

path(
    "inventory/history/",
    views.dashboard_inventory_history,
    name="dashboard_inventory_history",
),

path(
    "inventory/<int:pk>/stock-in/",
    views.dashboard_stock_in,
    name="dashboard_stock_in",
),

path(
    "inventory/<int:pk>/stock-out/",
    views.dashboard_stock_out,
    name="dashboard_stock_out",
),

path(
    "inventory/<int:pk>/adjust/",
    views.dashboard_stock_adjust,
    name="dashboard_stock_adjust",
),
# Analytics
path(
    "dashboard/analytics/",
    views.dashboard_analytics,
    name="dashboard_analytics",
),
path(
    "google-reviews/",
    views.google_reviews,
    name="dashboard_google_reviews"
),


path(
    "google-reviews/toggle/<int:id>/",
    views.toggle_google_review,
    name="toggle_google_review"
),

path(
    "orders/<str:order_id>/cancel/",
    views.cancel_order,
    name="cancel_order",
),
path(
    "google-reviews/delete/<int:id>/",
    views.delete_google_review,
    name="delete_google_review"
),
path(
    "processing-order/<int:order_id>/",
    views.processing_order,
    name="processing_order",
),
path(
    "orders/<str:order_id>/receipt/",
    views.order_receipt,
    name="order_receipt",
),
path("shop/", views.shop, name="shop"),
path(
    "brands/",
    views.brand_list,
    name="brands",
),
path("about/", views.about, name="about"),
path("ai/", views.ai_page, name="ai"),
path("ai/chat/", views.ai_chat, name="ai_chat"),
path(
        "blog/",
        views.blog_list,
        name="blog_list"
    ),


    # Single article
    path(
        "blog/<slug:slug>/",
        views.blog_detail,
        name="blog_detail"
    ),


    # Blog categories
    path(
        "blog/category/<slug:slug>/",
        views.blog_category,
        name="blog_category"
    ),

    path(
    "dashboard/blog/",
    views.dashboard_blog,
    name="dashboard_blog",
),
path(
    "dashboard/blog/add/",
    views.add_blog,
    name="dashboard_add_blog",
),
# Blog Categories
path(
    "dashboard/blog/categories/",
    views.dashboard_blog_categories,
    name="dashboard_blog_categories",
),

# Add Blog Category
path(
    "dashboard/blog/categories/add/",
    views.add_blog_category,
    name="dashboard_add_blog_category",
),

# Edit Blog Category
path(
    "dashboard/blog/categories/<int:pk>/edit/",
    views.edit_blog_category,
    name="dashboard_edit_blog_category",
),

# Delete Blog Category
path(
    "dashboard/blog/categories/<int:pk>/delete/",
    views.delete_blog_category,
    name="dashboard_delete_blog_category",
),

# Blog Tags
path(
    "dashboard/blog/tags/",
    views.dashboard_blog_tags,
    name="dashboard_blog_tags",
),
# ===========================
# BLOG DASHBOARD
# ===========================

path(
    "dashboard/blog/<int:blog_id>/edit/",
    views.edit_blog,
    name="dashboard_edit_blog",
),
path(
    "newsletter/subscribe/",
    views.newsletter_subscribe,
    name="newsletter_subscribe",
),

path(
    "dashboard/blog/<int:blog_id>/delete/",
    views.delete_blog,
    name="dashboard_delete_blog",
),
path(
    "dashboard/newsletter/",
    views.dashboard_newsletter_subscribers,
    name="dashboard_newsletter",
),

    path(
        "help-center/",
        views.help_center,
        name="help_center",
    ),

    path(
        "warranty/",
        views.warranty,
        name="warranty",
    ),

    path(
        "returns-refunds/",
        views.returns_refunds,
        name="returns_refunds",
    ),


    path(
        "faq/",
        views.faq,
        name="faq",
    ),

path(
    "staff/login/",
    views.staff_login,
    name="staff_login"
),

path(
    "staff/logout/",
    views.staff_logout,
    name="staff_logout"
),
path(
    "dashboard/account/",
    views.account_settings,
    name="account_settings"
),
path("request-quote/", views.request_quote, name="request_quote"),
path("request-quote/success/", views.quote_success, name="quote_success"),
path(
    "smartcontrol/account/",
    views.staff_account,
    name="staff_account"
),

path(
    "smartcontrol/account/password/",
    views.change_staff_password,
    name="change_staff_password"
),


    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password",
    ),

    path(
        "verify-reset-otp/",
        views.verify_reset_otp,
        name="verify_reset_otp",
    ),

    path(
        "new-password/",
        views.new_password,
        name="new_password",
    ),
# urls.py
path(
    "buy-now/<int:variant_id>/",
    views.buy_now,
    name="buy_now",
),
path(
    "dashboard/products/bulk/",
    views.dashboard_bulk_products,
    name="dashboard_bulk_products",
),
path(
    "ajax/featured-deals/",
    views.featured_deals_page,
    name="featured_deals_page",
),
path(
    "ajax/featured-products/",
    views.featured_products_ajax,
    name="featured_products_ajax",
),
    path(
        "shipping-policy/",
        views.shipping_policy,
        name="shipping_policy",
    ),

]
