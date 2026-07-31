import requests

from bs4 import BeautifulSoup

from .base import BaseImporter
from .jsonld import JsonLDParser
from ..product_schema import ImportedProduct


class GenericImporter(BaseImporter):

    supported_domains = []

    def import_product(self, url):

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        product = ImportedProduct()

        # Try to read structured product data (JSON-LD)
        structured = JsonLDParser.extract(soup)

        if structured:

            product.name = structured.get("name", "")

            product.description = structured.get(
                "description",
                ""
            )

            images = structured.get("image")

            if isinstance(images, list):
                product.images = images

            elif images:
                product.images = [images]

            brand = structured.get("brand")

            if isinstance(brand, dict):
                product.brand = brand.get("name", "")

            elif isinstance(brand, str):
                product.brand = brand

            offers = structured.get("offers")

            if isinstance(offers, dict):
                product.price = offers.get("price")

        else:
            # Fallback if no JSON-LD exists
            if soup.title:
                product.name = soup.title.text.strip()

        return product