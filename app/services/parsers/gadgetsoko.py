import json
import re

from .base import BaseParser


class GadgetSokoParser(BaseParser):
    """
    Dedicated parser for GadgetSoko.

    Strategy

    1. Schema.org JSON-LD
    2. OpenGraph
    3. HTML fallback
    """

    def parse(self):

        soup = self.get_soup()

        product = self.get_json_ld(soup)

        # =====================================================
        # METHOD 1
        # JSON-LD
        # =====================================================

        if product:

            brand = ""

            brand_obj = product.get("brand")

            if isinstance(brand_obj, dict):
                brand = brand_obj.get("name", "")

            elif isinstance(brand_obj, str):
                brand = brand_obj

            offers = product.get("offers", {})

            if isinstance(offers, list):
                offers = offers[0]

            availability = offers.get(
                "availability",
                ""
            )

            stock = 100

            if "OutOfStock" in availability:
                stock = 0

            images = self.extract_images_from_jsonld(
                product
            )

            if not images:
                images = self.extract_og_images(
                    soup
                )

            description = (
                product.get(
                    "description",
                    ""
                )
                or ""
            ).strip()

            return {

                "name": (
                    product.get(
                        "name",
                        ""
                    )
                    or ""
                ).strip(),

                "price": self.clean_price(
                    offers.get(
                        "price",
                        "0"
                    )
                ),

                "brand": brand,

                "category": product.get(
                    "category",
                    ""
                ),

                "description": description,

                "short_description": description[:250],

                "images": images,

                "stock": stock,

                "sku": product.get(
                    "sku",
                    ""
                ),

            }

        # =====================================================
        # METHOD 2
        # OpenGraph
        # =====================================================

        name = self.get_meta(
            soup,
            "og:title"
        )

        description = self.get_meta(
            soup,
            "og:description"
        )

        image = self.get_meta(
            soup,
            "og:image"
        )

        html = soup.get_text(" ")

        price = "0"

        # Kenyan price formats

        matches = re.findall(
            r"(?:KSh|KES)\s*([\d,]+(?:\.\d+)?)",
            html,
        )

        if matches:
            price = matches[0]

        images = []

        if image:
            images.append(image)

        return {

            "name": name,

            "price": self.clean_price(
                price
            ),

            "brand": "",

            "category": "",

            "description": description,

            "short_description": description[:250],

            "images": images,

            "stock": 0,

            "sku": "",

        }