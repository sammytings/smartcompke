import hashlib
import os

from django.core.files import File
from django.core.files.base import ContentFile

from app.models import ProductImage


class ImageSaver:

    @staticmethod
    def filename(url):

        return os.path.basename(
            url.split("?")[0]
        )

    @staticmethod
    def file_hash(file):

        file.seek(0)

        md5 = hashlib.md5()

        while True:

            chunk = file.read(8192)

            if not chunk:
                break

            md5.update(chunk)

        file.seek(0)

        return md5.hexdigest()

    @classmethod
    def save_product_image(

        cls,

        product,

        file,

        original_url,

        primary=False,

    ):

        name = cls.filename(original_url)

        # Skip duplicate filenames
        if ProductImage.objects.filter(
            product=product,
            image__endswith=name,
        ).exists():

            return

        if primary and not product.image:

            file.seek(0)

            product.image.save(

                name,

                File(file),

                save=False,

            )

            product.save(

                update_fields=["image"]

            )

            file.seek(0)

        gallery = ProductImage(

            product=product,

            alt_text=product.name,

            is_primary=primary,

        )

        gallery.image.save(

            name,

            ContentFile(file.read()),

            save=False,

        )

        gallery.save()