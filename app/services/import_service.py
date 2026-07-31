from decimal import Decimal, InvalidOperation

from django.db import transaction

from app.models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)

from .image_service import ImageService
from .parser_factory import ParserFactory
from .utils import (
    generate_unique_slug,
    generate_unique_sku,
)



class ProductImportService:

    """
    Product Import Pipeline

    URL
      ↓
    ParserFactory
      ↓
    Website Parser
      ↓
    Clean Product Data
      ↓
    Save Product
      ↓
    Save Variant
      ↓
    Save Gallery Images
    """



    def __init__(self, url):

        self.url = url



    # ---------------------------------------------------------
    # PRICE CLEANER
    # ---------------------------------------------------------

    def clean_price(self, value):

        if not value:

            return Decimal("0.00")


        value = str(value)

        value = (
            value
            .replace(",", "")
            .replace("KSh", "")
            .replace("KES", "")
            .strip()
        )


        try:

            return Decimal(value)


        except (InvalidOperation, ValueError):

            return Decimal("0.00")



    # ---------------------------------------------------------
    # STOCK CLEANER
    # ---------------------------------------------------------

    def clean_stock(self, value):

        try:

            return int(value)


        except:

            return 0



    # ---------------------------------------------------------
    # BRAND
    # ---------------------------------------------------------

    def get_brand(self, name):

        if not name:

            name = "Unknown"


        brand, _ = Brand.objects.get_or_create(

            name=name.strip()

        )


        return brand



    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    def get_category(self, name):

        if not name:

            name = "General"


        category, _ = Category.objects.get_or_create(

            name=name.strip()

        )


        return category



    # ---------------------------------------------------------
    # SAVE IMPORT
    # ---------------------------------------------------------

    @transaction.atomic
    def save(self):


        print("STARTING IMPORT")

        print(self.url)



        # ------------------------------
        # PARSE PRODUCT
        # ------------------------------

        parser = ParserFactory.get_parser(
            self.url
        )


        data = parser.parse()



        if not data:

            raise Exception(
                "Parser returned empty data."
            )



        if not data.get("name"):

            raise Exception(
                "Product name not found."
            )



        print(
            "PRODUCT DATA:",
            data
        )



        # ------------------------------
        # BRAND
        # ------------------------------

        brand = self.get_brand(

            data.get("brand")

        )



        # ------------------------------
        # CATEGORY
        # ------------------------------

        category = self.get_category(

            data.get("category")

        )



        # ------------------------------
        # DOWNLOAD IMAGES
        # ------------------------------

        image_urls = data.get(
            "images",
            []
        )


        gallery = ImageService.download_gallery(

            image_urls,

            limit=8

        )



        main_image = None


        if gallery:

            main_image = gallery[0]



        # ------------------------------
        # CREATE PRODUCT
        # ------------------------------

        product = Product.objects.create(

            name=data.get(
                "name"
            ),


            slug=generate_unique_slug(

                data.get("name")

            ),


            brand=brand,


            category=category,


            image=main_image,


            description=data.get(

                "description",

                ""

            ),


            short_description=data.get(

                "short_description",

                ""

            ),


            active=True,

        )



        print(
            "PRODUCT CREATED:",
            product.id
        )



        # ------------------------------
        # CREATE VARIANT
        # ------------------------------

        sku = generate_unique_sku(

            data.get("sku")

        )



        variant = ProductVariant.objects.create(

            product=product,


            sku=sku,


            stock=self.clean_stock(

                data.get("stock")

            ),


            price=self.clean_price(

                data.get("price")

            ),


            active=True,

        )



        print(
            "VARIANT CREATED:",
            variant.id
        )



        # ------------------------------
        # SAVE GALLERY
        # ------------------------------

        for image_path in gallery:


            ProductImage.objects.create(

                product=product,

                image=image_path,

            )



        print(
            "IMAGES SAVED:",
            len(gallery)
        )



        return product