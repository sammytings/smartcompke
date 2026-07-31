from pathlib import Path

from django.core.files import File
from django.db import transaction
from django.utils.text import get_valid_filename

from app.models import Product
from app.services.image_indexer import ImageIndexer
from app.services.image_matcher import ImageMatcher
from app.services.csv_image_mapper import CSVImageMapper


class ImageImporter:

    def __init__(self, media_folder, csv_file):

        self.indexer = ImageIndexer(media_folder)
        self.indexer.build()

        self.csv = CSVImageMapper(csv_file)
        self.csv.build()

        self.matcher = ImageMatcher(self.indexer)

        self.imported = 0
        self.skipped = 0
        self.missing = 0
        self.failed = 0


    @transaction.atomic
    def run(self):

        products = Product.objects.all().order_by("id")

        total = products.count()

        print()
        print("=" * 70)
        print(f"Found {total} products")
        print(f"Indexed {self.indexer.stats()['indexed']} images")
        print("=" * 70)
        print()


        for number, product in enumerate(products, start=1):

            print(f"[{number}/{total}] {product.name}")


            if product.image:

                self.skipped += 1

                print("   ✓ Already has image")

                continue



            try:

                image_path = self.find_image(product)


                if image_path is None:

                    self.missing += 1

                    print(
                        "   ✗ No image found - deleting product"
                    )

                    product.delete()

                    continue



                self.attach_image(
                    product,
                    image_path
                )


                self.imported += 1


                print(
                    f"   ✓ Imported {image_path.name}"
                )



            except Exception as e:

                self.failed += 1

                print(
                    f"   ⚠ Failed: {e}"
                )

                continue



        self.summary()



    def find_image(self, product):

        """
        Try to find the image in this order:

        1. Exact filename from CSV
        2. Exact normalized filename
        3. Partial filename
        4. Fuzzy matching
        """

        filename = self.csv.get_filename(product)



        if filename:

            stem = Path(filename).stem


            key = self.indexer.normalize(stem)



            # Exact normalized match
            if key in self.indexer.images:

                return self.indexer.images[key]



            # Partial match
            partial = self.indexer.search_partial(stem)


            if partial:

                return partial



        # Fuzzy matching fallback

        return self.matcher.match(product)





    def attach_image(self, product, image_path):

        """
        Attach image safely.

        Shortens long WordPress filenames
        to avoid SuspiciousFileOperation.
        """

        with open(image_path, "rb") as f:

            safe_name = get_valid_filename(
                image_path.name[:120]
            )


            product.image.save(
                safe_name,
                File(f),
                save=True
            )





    def summary(self):

        print()

        print("=" * 70)

        print("IMPORT COMPLETE")

        print("=" * 70)

        print(f"Imported : {self.imported}")

        print(f"Skipped  : {self.skipped}")

        print(f"Missing  : {self.missing}")

        print(f"Failed   : {self.failed}")

        print("=" * 70)