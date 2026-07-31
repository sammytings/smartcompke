from decimal import Decimal

from django.db import transaction
from django.utils.text import slugify

from app.models import (
    Brand,
    Category,
    Product,
    ProductVariant,
)

from .brands import BrandDetector
from .cleaner import HTMLCleaner
from .parser import WooCommerceParser


class WooCommerceImporter:

    def __init__(self, csv_file):

        self.parser = WooCommerceParser(csv_file)

        self.imported = 0
        self.updated = 0
        self.skipped = 0

    @transaction.atomic
    def run(self):

        for row in self.parser.rows():

            # Skip WooCommerce variations
            if row.get("Type", "").lower() == "variation":
                continue

            try:
                self.import_product(row)

            except Exception as e:

                self.skipped += 1

                print(f"✗ {row.get('Name')}")
                print(f"   {e}")

        self.summary()

    def import_product(self, row):

        name = row.get("Name", "").strip()

        if not name:
            return

        slug = slugify(name)

        category = self.get_category(row)

        brand = self.get_brand(row)

        product, created = Product.objects.update_or_create(

            slug=slug,

            defaults={

                "name": name,

                "category": category,

                "brand": brand,

                "short_description": self.short_description(row),

                "description": self.description(row),

                "featured": self.featured(row),

                "active": True,
            },
        )

        self.save_variant(product, row)

        self.save_image_urls(product, row)

        if created:

            self.imported += 1

            print(f"✓ Imported {product.name}")

        else:

            self.updated += 1

            print(f"↺ Updated {product.name}")

    def get_category(self, row):

        categories = row.get("Categories", "").strip()

        if not categories:
            return None

        category_name = categories.split(",")[0].strip()

        category, _ = Category.objects.get_or_create(

            name=category_name,

            defaults={

                "slug": slugify(category_name)
            },
        )

        return category

    def get_brand(self, row):

        brand = BrandDetector.detect(row)

        if not brand:
            return None

        if isinstance(brand, Brand):
            return brand

        brand, _ = Brand.objects.get_or_create(

            name=brand,

            defaults={

                "slug": slugify(brand)
            },
        )

        return brand

    def short_description(self, row):

        return HTMLCleaner.clean(

            row.get("Short description", "")

        )[:250]

    def description(self, row):

        return HTMLCleaner.clean(

            row.get("Description", "")

        )

    def featured(self, row):

        return row.get(

            "Is featured", ""

        ).lower() in [

            "1",
            "yes",
            "true",
        ]

    def decimal(self, value):

        if not value:
            return Decimal("0")

        try:

            return Decimal(

                str(value).replace(",", "")
            )

        except:

            return Decimal("0")

    def integer(self, value):

        try:
            return int(value)

        except:
            return 0

    def save_variant(self, product, row):

        sku = row.get("SKU", "").strip()

        if not sku:
            sku = f"SKU-{product.pk}"

        ProductVariant.objects.update_or_create(

            sku=sku,

            defaults={

                "product": product,

                "variant_name": "Default",

                "price": self.decimal(
                    row.get("Regular price")
                ),

                "discount_price": (
                    self.decimal(row.get("Sale price"))
                    if row.get("Sale price")
                    else None
                ),

                "stock": self.integer(
                    row.get("Stock")
                ),

                "active": True,
            },
        )

    def save_image_urls(self, product, row):

        """
        Save every WooCommerce image URL.
        Example:

        url1,url2,url3,url4
        """

        images = row.get("Images", "").strip()

        if not images:
            return

        image_urls = []

        for image in images.split(","):

            image = image.strip()

            if image:
                image_urls.append(image)

        # Requires a TextField called wordpress_images
        product.wordpress_images = "\n".join(image_urls)

        product.save(update_fields=["wordpress_images"])

    def summary(self):

        print()

        print("=" * 60)

        print("IMPORT COMPLETE")

        print("=" * 60)

        print(f"Imported : {self.imported}")

        print(f"Updated   : {self.updated}")

        print(f"Skipped   : {self.skipped}")

        print("=" * 60)