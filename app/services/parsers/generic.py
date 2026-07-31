import json
import re

from .base import BaseParser


class GenericParser(BaseParser):
    """
    Generic parser.

    Works for most ecommerce websites that expose:

    ✔ Schema.org Product JSON-LD
    ✔ OpenGraph metadata
    ✔ Standard HTML

    Examples:
        Amazon
        Alibaba
        AliExpress
        WooCommerce
        Shopify
        Magento
        Prestashop
        OpenCart
        BigCommerce
        Wix Stores
        Squarespace Commerce

    If a dedicated parser does not exist,
    ParserFactory will use this parser.
    """

    def parse(self):

        soup = self.get_soup()

        product = self.get_json_ld(soup)

        # --------------------------------------------------
        # JSON-LD FOUND
        # --------------------------------------------------

        if product:

            # -------------------------
            # Name
            # -------------------------

            name = (
                product.get("name")
                or self.get_meta(soup, "og:title")
                or ""
            ).strip()

            # -------------------------
            # Brand
            # -------------------------

            brand = ""

            brand_data = product.get("brand")

            if isinstance(brand_data, dict):
                brand = brand_data.get("name", "")

            elif isinstance(brand_data, str):
                brand = brand_data

            # -------------------------
            # Category
            # -------------------------

            category = product.get("category", "")

            # -------------------------
            # Description
            # -------------------------

            description = (
                product.get("description")
                or ""
            ).strip()

            short_description = description[:250]

            # -------------------------
            # SKU
            # -------------------------

            sku = product.get("sku", "")

            # -------------------------
            # Images
            # -------------------------

            images = self.extract_images_from_jsonld(product)

            if not images:
                images = self.extract_og_images(soup)

            # -------------------------
            # Price
            # -------------------------

            price = "0"

            offers = product.get("offers")

            if isinstance(offers, dict):

                price = (
                    offers.get("price")
                    or offers.get("lowPrice")
                    or "0"
                )

                availability = offers.get(
                    "availability",
                    "",
                )

            elif isinstance(offers, list):

                first_offer = offers[0]

                price = (
                    first_offer.get("price")
                    or first_offer.get("lowPrice")
                    or "0"
                )

                availability = first_offer.get(
                    "availability",
                    "",
                )

            else:

                availability = ""

            price = self.clean_price(price)

            # -------------------------
            # Stock
            # -------------------------

            stock = 0

            if "instock" in availability.lower():
                stock = 100

            # -------------------------
            # Return
            # -------------------------

            return {

                "name": name,

                "price": price,

                "brand": brand,

                "category": category,

                "description": description,

                "short_description": short_description,

                "images": images,

                "stock": stock,

                "sku": sku,

            }

        # ==================================================
        # FALLBACK USING OPENGRAPH + HTML
        # ==================================================

        name = self.get_meta(
            soup,
            "og:title",
        )

        description = self.get_meta(
            soup,
            "og:description",
        )

        image = self.get_meta(
            soup,
            "og:image",
        )

        price = "0"

        html = soup.get_text(" ")

        # Try to locate a price

        matches = re.findall(
            r"(?:KES|KSh|USD|\$)?\s?([\d,]+\.\d+)",
            html,
        )

        if matches:
            price = matches[0].replace(",", "")

        images = []

        if image:
            images.append(image)

        # Try title tag

        if not name and soup.title:
            name = soup.title.text.strip()

        return {

            "name": name,

            "price": price,

            "brand": "",

            "category": "",

            "description": description,

            "short_description": description[:250],

            "images": images,

            "stock": 0,

            "sku": "",

        }