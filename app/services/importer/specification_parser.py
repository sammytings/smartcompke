import re

from bs4 import BeautifulSoup

from app.models import (
    ProductVariant,
    Specification,
    VariantSpecification,
)


class SpecificationParser:

    @classmethod
    def save(cls, product, html):

        if not html:
            return

        variant = product.variants.first()

        if variant is None:

            variant = ProductVariant.objects.create(
                product=product,
                sku=product.slug,
                variant_name="Default",
                price=product.price,
                stock=0,
            

        soup = BeautifulSoup(html, "html.parser")

        cls.from_tables(variant, soup)
        cls.from_lists(variant, soup)
        cls.from_paragraphs(variant, soup)

    # --------------------------------------------------

    @classmethod
    def from_tables(cls, variant, soup):

        for table in soup.find_all("table"):

            for row in table.find_all("tr"):

                cols = row.find_all(["td", "th"])

                if len(cols) < 2:
                    continue

                key = cols[0].get_text(" ", strip=True)
                value = cols[1].get_text(" ", strip=True)

                cls.create(
                    variant,
                    key,
                    value,
                )

    # --------------------------------------------------

    @classmethod
    def from_lists(cls, variant, soup):

        for ul in soup.find_all(["ul", "ol"]):

            for li in ul.find_all("li"):

                text = li.get_text(" ", strip=True)

                if ":" not in text:
                    continue

                key, value = text.split(":", 1)

                cls.create(
                    variant,
                    key,
                    value,
                )

    # --------------------------------------------------

    @classmethod
    def from_paragraphs(cls, variant, soup):

        for p in soup.find_all("p"):

            text = p.get_text(" ", strip=True)

            if ":" not in text:
                continue

            if len(text) > 150:
                continue

            key, value = text.split(":", 1)

            cls.create(
                variant,
                key,
                value,
            )

    # --------------------------------------------------

    @classmethod
    def create(
        cls,
        variant,
        key,
        value,
    ):

        key = cls.clean(key)
        value = cls.clean(value)

        if not key or not value:
            return

        specification, _ = Specification.objects.get_or_create(
            category=variant.product.category,
            name=key,
            defaults={
                "position": 0,
            },
        )

        VariantSpecification.objects.update_or_create(
            variant=variant,
            specification=specification,
            defaults={
                "value": value,
            },
        )

    # --------------------------------------------------

    @staticmethod
    def clean(text):

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()