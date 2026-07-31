from decimal import Decimal

from django.db import transaction
from django.utils.text import slugify

from app.models import Product, ProductVariant

from .brand_detector import BrandDetector
from .category_service import CategoryService
from .cleaner import HTMLCleaner
from .specification_parser import SpecificationParser


class ProductImporter:

    @classmethod
    @transaction.atomic
    def import_product(cls, row):

        name = row.get("Name", "").strip()

        if not name:
            return None

        slug = slugify(name)

        description = HTMLCleaner.clean(
            row.get("Description", "")
        )

        short_description = HTMLCleaner.short_description(
            row.get("Short description", "")
            or description
        )

        product, created = Product.objects.update_or_create(

            slug=slug,

            defaults={

                "name": name,

                "category": CategoryService.get_category(row),

                "brand": BrandDetector.detect(row),

                "description": description,

                "short_description": short_description,

                "featured": cls.featured(row),

                "active": True,

                "wordpress_images": cls.image_urls(row),
            },
        )

        cls.variant(product, row)

        SpecificationParser.save(
            product,
            description,
        )

        return product

    # -----------------------------------------------------

    @classmethod
    def variant(cls, product, row):

        sku = row.get("SKU", "").strip()

        if not sku:
            sku = f"SKU-{product.pk}"

        ProductVariant.objects.update_or_create(

            sku=sku,

            defaults={

                "product": product,

                "variant_name": "Default",

                "price": cls.money(
                    row.get("Regular price")
                ),

                "discount_price": cls.sale_price(row),

                "stock": cls.integer(
                    row.get("Stock")
                ),

                "active": True,
            },
        )

    # -----------------------------------------------------

    @staticmethod
    def image_urls(row):

        images = row.get("Images", "").strip()

        if not images:
            return ""

        urls = []

        seen = set()

        for url in images.split(","):

            url = url.strip()

            if not url:
                continue

            if url in seen:
                continue

            seen.add(url)

            urls.append(url)

        return "\n".join(urls)

    # -----------------------------------------------------

    @staticmethod
    def featured(row):

        value = row.get(
            "Is featured?",
            "",
        ).lower()

        return value in (
            "1",
            "yes",
            "true",
        )

    # -----------------------------------------------------

    @staticmethod
    def money(value):

        if not value:
            return Decimal("0")

        try:

            return Decimal(
                value.replace(",", "")
            )

        except Exception:

            return Decimal("0")

    # -----------------------------------------------------

    @classmethod
    def sale_price(cls, row):

        sale = row.get(
            "Sale price",
            "",
        )

        if not sale:
            return None

        value = cls.money(sale)

        if value <= 0:
            return None

        return value

    # -----------------------------------------------------

    @staticmethod
    def integer(value):

        try:
            return int(value)
        except Exception:
            return 0