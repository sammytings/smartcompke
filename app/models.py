from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# ==========================
# CATEGORY
# ==========================
from django.db import models
from django.utils.text import slugify
def send_order_email(order, subject, template):

    html_message = render_to_string(
        template,
        {
            "order": order
        }
    )

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    icon = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.filter(active=True).count()

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
# ==========================
# BRAND
# ==========================

from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    # Brand Logo
    logo = models.ImageField(
        upload_to="brands/logos/",
        blank=True,
        null=True
    )

    # Hero Banner
    banner = models.ImageField(
        upload_to="brands/banners/",
        blank=True,
        null=True
    )

    # Brand Information
    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Example: Official HP Store"
    )

    short_description = models.TextField(
        blank=True,
        help_text="Short introduction displayed on the brand page."
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    founded = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True
    )

    warranty = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: 12 Months Manufacturer Warranty"
    )

    theme_color = models.CharField(
        max_length=7,
        default="#1E4FD8",
        help_text="Primary brand color in HEX."
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

# ==========================
# PRODUCT CONDITIONS
# ==========================

CONDITIONS = (
    ("new", "New"),
    ("exuk", "Ex-UK"),
    ("refurbished", "Refurbished"),
)


# ==========================
# WARRANTY
# ==========================

WARRANTIES = (
    ("3 Months", "3 Months"),
    ("6 Months", "6 Months"),
    ("12 Months", "12 Months"),
    ("24 Months", "24 Months"),
    ("36 Months", "36 Months"),
    ("5 Years", "5 Years"),
    ("Lifetime", "Lifetime"),
)


# ==========================
# PRODUCT
# ==========================

from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
    
class Product(models.Model):

    VAT_RATE = Decimal("0.16")

    name = models.CharField(max_length=250)

    slug = models.SlugField(
        max_length=255,
        null=True,
        db_index=True,
    )
    wordpress_images = models.TextField(
    blank=True,
    default=""
)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    image = models.ImageField(
    upload_to="products/",
    blank=True,
    null=True,
    max_length=500
)

    short_description = models.CharField(max_length=250)

    description = models.TextField(blank=True)

    condition = models.CharField(
        max_length=20,
        choices=CONDITIONS,
        blank=True,
    )

    warranty = models.CharField(
        max_length=30,
        choices=WARRANTIES,
        default="12 Months",
    )

    vat_inclusive = models.BooleanField(
        default=True,
        verbose_name="Price Includes VAT",
    )

    featured = models.BooleanField(default=False)

    new_arrival = models.BooleanField(default=False)

    trending = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    @property
    def default_variant(self):
        return (
            self.variants
            .filter(active=True)
            .order_by("id")
            .first()
        )
    @property
    def in_stock(self):
        return self.variants.filter(
            active=True,
            stock__gt=0
        ).exists()
    @property
    def sku(self):
        variant = self.default_variant
        return variant.sku if variant else ""

    @property
    def stock(self):
        variant = self.default_variant
        return variant.stock if variant else 0

    @property
    def price(self):
        variant = self.default_variant
        return variant.price if variant else Decimal("0.00")

    @property
    def current_price(self):
        variant = self.default_variant
        return variant.current_price if variant else Decimal("0.00")

    @property
    def discount_price(self):
        variant = self.default_variant
        return variant.discount_price if variant else None

    @property
    def discount_start(self):
        variant = self.default_variant
        return variant.discount_start if variant else None

    @property
    def discount_end(self):
        variant = self.default_variant
        return variant.discount_end if variant else None

    @property
    def price_including_vat(self):
        variant = self.default_variant
        return (
            variant.price_including_vat
            if variant else Decimal("0.00")
        )

    @property
    def price_excluding_vat(self):
        variant = self.default_variant
        return (
            variant.price_excluding_vat
            if variant else Decimal("0.00")
        )

    @property
    def vat_amount(self):
        variant = self.default_variant
        return (
            variant.vat_amount
            if variant else Decimal("0.00")
        )
    
    @property
    def price_with_vat(self):
        variant = self.default_variant
        if variant:
            return variant.price_including_vat
        return 0


    @property
    def price_without_vat(self):
        variant = self.default_variant
        if variant:
            return variant.price_excluding_vat
        return 0


    @property
    def discount_price_with_vat(self):
        variant = self.default_variant
        if variant and variant.discount_active:
            return variant.price_including_vat
        return None


    @property
    def discount_price_without_vat(self):
        variant = self.default_variant
        if variant and variant.discount_active:
            return variant.price_excluding_vat
        return None
    @property
    def conversion_rate(self):

        views = self.analytics_events.filter(
            event_type=AnalyticsEvent.VIEW
        ).count()

        purchases = self.analytics_events.filter(
            event_type=AnalyticsEvent.PURCHASE
    ).count()

        if views == 0:
            return 0

        return round((purchases / views) * 100, 2)
# ==========================
# CATEGORY SPECIFICATIONS
# Fully dynamic: each Category owns its own set of Specification
# names, defined and reordered entirely from the Django admin.
# Example:
#   Laptop  -> RAM, Processor, Storage, Generation
#   Monitor -> Display, Resolution, Curved, Panel Type
# ==========================

class Specification(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="specifications"
    )

    name = models.CharField(max_length=100)

    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.category.name} - {self.name}"
from django.db import models
from django.utils import timezone
from django.db import models
from django.utils import timezone


class DealCampaign(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("active", "Active"),
        ("ended", "Ended"),
    )

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    holder_image = models.ImageField(
        upload_to="campaigns/holders/"
    )

    banner = models.ImageField(
        upload_to="campaigns/banners/",
        blank=True,
        null=True
    )

    products = models.ManyToManyField(
        "ProductVariant",
        related_name="deal_campaigns",
        blank=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=(
            ("percent", "Percentage"),
            ("fixed", "Fixed Amount"),
            ("price", "Fixed Price"),
        ),
        default="percent"
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    active = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def total_products(self):
        return self.products.count()

    @property
    def is_running(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date
from decimal import Decimal
class ProductVariant(models.Model):

    VAT_RATE = Decimal("0.16")

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    image = models.ImageField(
        upload_to="variants/",
        blank=True,
        null=True
    )
    

    variant_name = models.CharField(
        max_length=255,
        blank=True
    )
    deal_campaign = models.ForeignKey(
        DealCampaign,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants"
)
    stock = models.PositiveIntegerField(default=0)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    discount_start = models.DateTimeField(
        blank=True,
        null=True
    )

    discount_end = models.DateTimeField(
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

    def money(self, value):
        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    from decimal import Decimal


    @property
    def current_price(self):

        if self.discount_active:
            return self.discount_price

        return self.price
    @property
    def final_price(self):
        return self.current_price
    @property
    def price_without_vat(self):
        """
            Returns the selling price excluding VAT.
    """
        if self.product.vat_inclusive:
            return self.current_price / (Decimal("1.00") + self.VAT_RATE)

        return self.current_price
    @property
    def original_price_without_vat(self):
        """
    Original price excluding VAT.
    """
        if self.product.vat_inclusive:
            return self.price / (Decimal("1.00") + self.VAT_RATE)

        return self.price
    @property
    def price_including_vat(self):

        if self.product.vat_inclusive:
            return self.money(self.current_price)

        return self.money(
            self.current_price *
            (Decimal("1.00") + self.VAT_RATE)
        )

    @property
    def price_excluding_vat(self):

        if self.product.vat_inclusive:
            return self.money(
                self.current_price /
                (Decimal("1.00") + self.VAT_RATE)
            )

        return self.money(self.current_price)

    @property
    def vat_amount(self):

        return self.money(
            self.price_including_vat -
            self.price_excluding_vat
        )

    @property
    def amount_saved(self):

        if self.discount_active:
            return self.money(
                self.price -
                self.discount_price
            )

        return Decimal("0.00")
    from decimal import Decimal
    from django.utils import timezone

    @property
    def discount_active(self):
        if (
            self.discount_price is None or
            self.discount_start is None or
            self.discount_end is None
    ):
            return False

        now = timezone.now()

        return self.discount_start <= now <= self.discount_end


    @property
    def discount_percent(self):
        if (
            self.discount_price is None or
            self.price is None or
            self.price <= 0
    ):
            return 0

        discount = (
            (self.price - self.discount_price)
            / self.price
        ) * Decimal("100")

        return round(discount)


# ==========================
# VARIANT SPECIFICATIONS
# Links one ProductVariant to a Specification + chosen value.
# The Specification/Value choices offered in the admin are
# filtered dynamically to the variant's product's category
# (see admin.py + static/admin/js/variant_specs.js).
# ==========================
from django.conf import settings


class MarketingCampaign(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("sending", "Sending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    title = models.CharField(
        max_length=255
    )

    subject = models.CharField(
        max_length=255
    )

    message = models.TextField(
        blank=True
    )

    products = models.ManyToManyField(
        "Product",
        related_name="marketing_campaigns",
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_products = models.PositiveIntegerField(
        default=0
    )

    total_recipients = models.PositiveIntegerField(
        default=0
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )

    email = models.EmailField(
        unique=True
    )

    first_login = models.DateTimeField(
        auto_now_add=True
    )

    last_login = models.DateTimeField(
        auto_now=True
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.email
class VariantSpecification(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE
    )

    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("variant", "specification")

    def __str__(self):
        return f"{self.specification.name}: {self.value}"


# ==========================
# PRODUCT GALLERY
# related_name is "gallery" — product_detail.html must use
# product.gallery.all (NOT product.gallery_images.all).
# ==========================

from django.db import models


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="gallery"
    )

    image = models.ImageField(
        upload_to="gallery/"
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-is_primary", "uploaded_at"]

    def __str__(self):
        return f"{self.product.name} ({'Primary' if self.is_primary else 'Gallery'})"
    @property
    def primary_image(self):
        """
    Returns the primary gallery image.
    Falls back to the first gallery image.
    Finally falls back to the legacy product.image field.
        """

        image = self.gallery.filter(is_primary=True).first()

        if image:
            return image

        image = self.gallery.first()

        if image:
            return image

        if self.image:
            return self.image

        return None
# ==========================
# PRODUCT REVIEWS
# (product.reviews.all, review.customer_initials, review.star_display,
# review.verified, average_rating, review_count).
# ==========================

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    customer_name = models.CharField(max_length=120)

    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5
    )

    comment = models.TextField()

    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} — {self.product.name} ({self.rating}★)"

    @property
    def customer_initials(self):
        parts = self.customer_name.split()
        if not parts:
            return "?"
        return "".join(p[0].upper() for p in parts[:2])

    @property
    def star_display(self):
        return "★" * self.rating + "☆" * (5 - self.rating)


from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated"]

    def __str__(self):

        if self.user:
            return f"{self.user.username}'s Cart"

        return f"Guest Cart ({self.session_key})"

    @property
    def subtotal(self):
        """
        Total value of all active cart items.
        """
        return sum(
            item.subtotal
            for item in self.items.filter(
                saved_for_later=False
            )
        )

    @property
    def total_items(self):
        """
        Total quantity of all active cart items.
        """
        return sum(
            item.quantity
            for item in self.items.filter(
                saved_for_later=False
            )
        )

    @property
    def total_unique_items(self):
        """
        Number of different products in the cart.
        """
        return self.items.filter(
            saved_for_later=False
        ).count()

    @property
    def saved_items(self):
        """
        Number of items saved for later.
        """
        return self.items.filter(
            saved_for_later=True
        ).count()

    @property
    def is_guest(self):
        return self.user is None

    @property
    def is_empty(self):
        return self.total_items == 0
class SpecificationOption(models.Model):
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        related_name="options",
    )

    value = models.CharField(max_length=100)

    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "value"]

    def __str__(self):
        return self.value


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)
    include_vat = models.BooleanField(default=False)

    saved_for_later = models.BooleanField(default=False)

    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")

    def __str__(self):
        return self.product.name

    @property
    def price(self):
        if self.variant:
            return self.variant.current_price
        return self.product.current_price

    @property
    def subtotal(self):
        return self.price * self.quantity


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlist",
    )

    session_key = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Wishlist"
        return f"Guest Wishlist ({self.session_key})"
class WishlistItem(models.Model):

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist","product","variant")

    def __str__(self):
        return self.product.name


# ==========================
# ORDER
# ==========================
import random
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):

    PAYMENT_CHOICES = (
        ("mpesa", "M-Pesa"),
        ("card", "Card"),
        ("cod", "Cash on Delivery"),
    )

    DELIVERY_CHOICES = (
        ("standard", "Standard Delivery"),
        ("express", "Express Delivery"),
        ("pickup", "Store Pickup"),
    )

    VAT_CHOICES = (
        ("exclusive", "VAT Exclusive"),
        ("inclusive", "VAT Inclusive"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    order_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
)

    full_name = models.CharField(max_length=200)

    email = models.EmailField()

    phone = models.CharField(max_length=30)

    address = models.TextField()

    city = models.CharField(max_length=120)

    county = models.CharField(max_length=120)

    postcode = models.CharField(
        max_length=20,
        blank=True
    )

    notes = models.TextField(blank=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES
    )

    vat_option = models.CharField(
        max_length=20,
        choices=VAT_CHOICES,
        default="exclusive"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    cancellation_reason = models.TextField(
        blank=True
    )

    admin_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.order_id:

            while True:

                code = f"SCK-{random.randint(100000,999999)}"

                if not Order.objects.filter(order_id=code).exists():

                    self.order_id = code

                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


    price = models.DecimalField(max_digits=10, decimal_places=2)

    total = models.DecimalField(max_digits=10, decimal_places=2)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    address = models.TextField(blank=True)
    google_picture = models.URLField(blank=True, null=True)   # new
    date_created = models.DateTimeField(auto_now_add=True)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class EmailOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_otps"
    )

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    
from django.db import models
from django.core.exceptions import ValidationError


class Banner(models.Model):

    BANNER_TYPES = [
        ("home", "Homepage"),
        ("deal", "Deals"),

        ("category", "Specific Category Banner"),
        ("category_global", "All Categories Banner"),
        ("category_slider", "Category Slider"),

        ("brand", "Brand"),
        ("promo", "Promotion"),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)

    image = models.ImageField(upload_to="banners/")

    button_text = models.CharField(
        max_length=50,
        blank=True
    )

    button_link = models.CharField(
        max_length=255,
        blank=True
    )

    banner_type = models.CharField(
        max_length=20,
        choices=BANNER_TYPES
    )

    category = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="banners",
    )

    brand = models.ForeignKey(
        "Brand",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="banners"
    )

    background_color = models.CharField(
        max_length=20,
        default="#ffffff"
    )

    text_color = models.CharField(
        max_length=20,
        default="#000000"
    )

    order = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)

    start_date = models.DateTimeField(null=True, blank=True)

    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

    def clean(self):

        if self.banner_type == "category" and not self.category:
            raise ValidationError(
                "Please select a category for a specific category banner."
            )

        if self.banner_type in [
            "category_global",
            "category_slider",
            "home",
            "deal",
            "promo",
        ]:
            self.category = None

        if self.banner_type != "brand":
            self.brand = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class InventoryTransaction(models.Model):
    STOCK_IN = "IN"
    STOCK_OUT = "OUT"
    ADJUSTMENT = "ADJUST"

    TRANSACTION_TYPES = [
        (STOCK_IN, "Stock In"),
        (STOCK_OUT, "Stock Out"),
        (ADJUSTMENT, "Adjustment"),
    ]

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="inventory_transactions"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    quantity = models.IntegerField()

    balance_after = models.IntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.utils import timezone


class AnalyticsEvent(models.Model):

    VIEW = "view"
    CART = "cart"
    WISHLIST = "wishlist"
    CHECKOUT = "checkout"
    PURCHASE = "purchase"
    SEARCH = "search"

    EVENT_TYPES = (
        (VIEW, "Product View"),
        (CART, "Add To Cart"),
        (WISHLIST, "Wishlist"),
        (CHECKOUT, "Checkout"),
        (PURCHASE, "Purchase"),
        (SEARCH, "Search"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="analytics_events",
        null=True,
        blank=True,
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        related_name="analytics_events",
        null=True,
        blank=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="analytics_events",
        null=True,
        blank=True,
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    session_key = models.CharField(
        max_length=120,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    referer = models.URLField(
        blank=True,
    )

    search_query = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.product:
            return f"{self.get_event_type_display()} - {self.product.name}"
        return self.get_event_type_display()
    from decimal import Decimal


class ProductAnalytics(models.Model):

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="analytics"
    )

    total_views = models.PositiveIntegerField(default=0)

    wishlist_adds = models.PositiveIntegerField(default=0)

    cart_adds = models.PositiveIntegerField(default=0)

    checkout_count = models.PositiveIntegerField(default=0)

    total_sales = models.PositiveIntegerField(default=0)

    abandoned_carts = models.PositiveIntegerField(default=0)

    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    last_viewed = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-total_views"]

    def __str__(self):
        return self.product.name

    @property
    def conversion_rate(self):
        if self.total_views == 0:
            return 0

        return round(
            (self.total_sales / self.total_views) * 100,
            2
        )
class GoogleReview(models.Model):

    reviewer_name = models.CharField(
        max_length=200
    )

    reviewer_photo = models.URLField(
        blank=True,
        null=True
    )

    rating = models.PositiveIntegerField(
        default=5
    )

    comment = models.TextField()

    google_review_id = models.CharField(
        max_length=255,
        unique=True
    )

    review_time = models.DateTimeField(
        blank=True,
        null=True
    )

    is_visible = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        ordering = [
            "-review_time",
            "-created_at"
        ]


    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}★)"

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import math

User = get_user_model()
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import math

User = get_user_model()
# ==============================================================================
# BLOG CATEGORY
# ==============================================================================

from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class BlogCategory(models.Model):

    name = models.CharField(
        max_length=120,
        unique=True
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="blog/categories/",
        blank=True,
        null=True
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="FontAwesome icon class"
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):

        if not self.slug:

            slug = slugify(self.name)

            unique_slug = slug

            counter = 1

            while BlogCategory.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():

                unique_slug = f"{slug}-{counter}"

                counter += 1

            self.slug = unique_slug

        if not self.meta_title:
            self.meta_title = self.name

        if not self.meta_description:
            self.meta_description = self.description[:160]

        super().save(*args, **kwargs)

    def get_absolute_url(self):

        return reverse(
            "blog_category",
            kwargs={"slug": self.slug}
        )

    def __str__(self):

        return self.name


# ==============================================================================
# BLOG TAG
# ==============================================================================


class BlogTag(models.Model):

    name = models.CharField(
        max_length=80,
        unique=True
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.slug:

            slug = slugify(self.name)

            unique_slug = slug

            counter = 1

            while BlogTag.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():

                unique_slug = f"{slug}-{counter}"

                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name


# ==============================================================================
# NEWSLETTER SUBSCRIBERS
# ==============================================================================


class NewsletterSubscriber(models.Model):

    email = models.EmailField(
        unique=True
    )

    active = models.BooleanField(
        default=True
    )

    subscribed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):

        return self.email
    
# ==============================================================================
# BLOG POST
# ==============================================================================

import math

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class BlogPost(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("review", "Pending Review"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
    )

    title = models.CharField(
        max_length=250
    )

    slug = models.SlugField(
        max_length=260,
        unique=True,
        blank=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts"
    )

    tags = models.ManyToManyField(
        BlogTag,
        blank=True
    )

    image = models.ImageField(
        upload_to="blog/posts/",
        blank=True,
        null=True
    )

    excerpt = models.TextField(
        max_length=500
    )

    content = CKEditor5Field(
        "Article Content",
        config_name="default"
    )

    related_products = models.ManyToManyField(
        "Product",
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    featured = models.BooleanField(
        default=False
    )

    allow_comments = models.BooleanField(
        default=True
    )

    # -------------------------
    # SEO
    # -------------------------

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    meta_keywords = models.CharField(
        max_length=300,
        blank=True
    )

    canonical_url = models.URLField(
        blank=True,
        null=True
    )

    # -------------------------
    # Statistics
    # -------------------------

    word_count = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    reading_time = models.PositiveIntegerField(
        default=1,
        editable=False
    )

    views = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    likes = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    shares = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    # -------------------------
    # Dates
    # -------------------------

    published_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-featured",
            "-published_at",
            "-created_at",
        ]

        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["featured"]),
        ]

    def generate_unique_slug(self):

        slug = slugify(self.title)

        unique_slug = slug

        counter = 1

        while BlogPost.objects.filter(
            slug=unique_slug
        ).exclude(
            pk=self.pk
        ).exists():

            unique_slug = f"{slug}-{counter}"

            counter += 1

        return unique_slug

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = self.generate_unique_slug()

        text = strip_tags(self.content or "")

        self.word_count = len(text.split())

        self.reading_time = max(
            1,
            math.ceil(self.word_count / 200)
        )

        if (
            self.status == "published"
            and self.published_at is None
        ):
            self.published_at = timezone.now()

        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            self.meta_description = self.excerpt[:160]

        if not self.meta_keywords:
            self.meta_keywords = ", ".join(
                self.title.split()
            )

        super().save(*args, **kwargs)

        if not self.canonical_url:

            self.canonical_url = (
                f"https://smartcomputerske.com"
                f"{self.get_absolute_url()}"
            )

            super().save(
                update_fields=["canonical_url"]
            )

    def get_absolute_url(self):

        return reverse(
            "blog_detail",
            kwargs={
                "slug": self.slug
            }
        )

    @property
    def comments_count(self):

        return self.comments.filter(
            approved=True
        ).count()

    def __str__(self):

        return self.title

from django.db import models
from django.utils.text import slugify


class Deal(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="deals"
    )

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_start = models.DateTimeField()

    discount_end = models.DateTimeField()


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    active = models.BooleanField(
        default=True
    )


    def __str__(self):
        return f"{self.product.name} Deal"


    @property
    def is_active(self):

        from django.utils import timezone

        now = timezone.now()

        return (
            self.active
            and
            self.discount_start <= now <= self.discount_end
        )


    @property
    def discount_percentage(self):

        if self.old_price:

            return round(
                (
                    (self.old_price - self.new_price)
                    /
                    self.old_price
                ) * 100
            )

        return 0

from django.contrib.auth.models import User
from django.db import models


class StaffProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    profile_image = models.ImageField(
        upload_to="staff_profiles/",
        default="staff_profiles/default.png",
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return self.user.username