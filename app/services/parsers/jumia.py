import json
import re

from .base import BaseParser


class JumiaParser(BaseParser):
    """
    Dedicated parser for Jumia.

    Uses multiple fallbacks.

    Priority:

    1. Schema.org JSON-LD
    2. Jumia embedded JSON
    3. OpenGraph
    4. HTML
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
                product.get("description", "")
                or ""
            ).strip()

            return {

                "name": (
                    product.get("name", "")
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
        # Embedded JSON
        # =====================================================

        scripts = soup.find_all("script")

        for script in scripts:

            text = script.string

            if not text:
                continue

            if '"sku"' not in text:
                continue

            try:

                match = re.search(
                    r'(\{.*"sku".*\})',
                    text,
                    re.S
                )

                if not match:
                    continue

                obj = json.loads(
                    match.group(1)
                )

                if not isinstance(
                    obj,
                    dict
                ):
                    continue

                images = []

                gallery = obj.get(
                    "images",
                    []
                )

                for img in gallery:

                    if isinstance(
                        img,
                        str
                    ):

                        if img.startswith("//"):
                            img = "https:" + img

                        images.append(img)

                return {

                    "name": obj.get(
                        "name",
                        ""
                    ),

                    "price": self.clean_price(
                        obj.get(
                            "price",
                            "0"
                        )
                    ),

                    "brand": obj.get(
                        "brand",
                        ""
                    ),

                    "category": obj.get(
                        "category",
                        ""
                    ),

                    "description": obj.get(
                        "description",
                        ""
                    ),

                    "short_description": (
                        obj.get(
                            "description",
                            ""
                        )[:250]
                    ),

                    "images": images,

                    "stock": 100,

                    "sku": obj.get(
                        "sku",
                        ""
                    ),

                }

            except Exception:
                pass

        # =====================================================
        # METHOD 3
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

        prices = re.findall(
            r"KSh\s*([\d,]+\.\d+)",
            html
        )

        if prices:
            price = prices[0]

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