import os

from django.core.files.base import ContentFile

from .iconify_provider import IconifyProvider


class CategoryIconService:

    @classmethod
    def assign_icon(cls, category):

        if category.icon:
            return

        svg = IconifyProvider.search(category.name)

        if not svg:
            print("No icon found.")
            return

        filename = (
            category.name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            + ".svg"
        )

        category.icon.save(
            filename,
            ContentFile(svg.encode("utf-8")),
            save=True,
        )

        print("Saved:", filename)