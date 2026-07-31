from pathlib import Path

from django.core.files import File
from django.db import transaction

from app.models import ProductImage


class ImageSaver:
    """
    Saves downloaded images.

    • First image -> Product.image
    • All images -> ProductImage gallery
    • Prevents duplicate gallery entries
    """

    @classmethod
    @transaction.atomic
    def save_product_image(
        cls,
        product,
        file,
        filename,
        primary=False,
    ):

        filename = cls.clean_filename(filename)

        # ---------------------------------------
        # Duplicate check
        # ---------------------------------------

        if ProductImage.objects.filter(
            product=product,
            image__icontains=filename,
        ).exists():
            return

        # ---------------------------------------
        # Save featured image
        # ---------------------------------------

        if primary:

            if (
                not product.image
                or not product.image.name
            ):

                file.seek(0)

                product.image.save(

                    filename,

                    File(file),

                    save=False,
                )

                product.save(
                    update_fields=[
                        "image",
                    ]
                )

        # ---------------------------------------
        # Gallery image
        # ---------------------------------------

        file.seek(0)

        image = ProductImage(

            product=product,

            alt_text=product.name,

            is_primary=primary,
        )

        image.image.save(

            filename,

            File(file),

            save=True,
        )

    # ---------------------------------------------

    @staticmethod
    def clean_filename(filename):

        filename = Path(filename).name

        filename = filename.replace("%20", "-")

        filename = filename.replace(" ", "-")

        if len(filename) > 180:

            stem = Path(filename).stem[:140]

            suffix = Path(filename).suffix

            filename = stem + suffix

        return filename