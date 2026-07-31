from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand

from app.models import Product
from app.services.importer.image_downloader import ImageDownloader
from app.services.importer.image_writer import ImageWriter


class Command(BaseCommand):
    help = "Download all WooCommerce product images"

    DOWNLOAD_THREADS = 20

    def handle(self, *args, **options):

        products = Product.objects.exclude(
            wordpress_images=""
        ).exclude(
            wordpress_images__isnull=True
        )

        total_products = products.count()

        total_images = sum(
            len(
                [
                    x
                    for x in p.wordpress_images.splitlines()
                    if x.strip()
                ]
            )
            for p in products
        )

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(f"{total_products} products")
        self.stdout.write(f"{total_images} images")
        self.stdout.write("=" * 70)

        queue = Queue()

        writer = ImageWriter(queue)
        writer.start()

        downloader = ImageDownloader()

        completed = 0

        with ThreadPoolExecutor(
            max_workers=self.DOWNLOAD_THREADS
        ) as executor:

            futures = {
                executor.submit(
                    downloader.download_product,
                    product,
                ): product
                for product in products
            }

            for future in as_completed(futures):

                product = futures[future]

                try:

                    jobs = future.result()

                    for job in jobs:

                        queue.put(job)

                except Exception as e:

                    self.stdout.write(
                        self.style.ERROR(
                            f"{product.name}\n{e}"
                        )
                    )

                completed += 1

                if completed % 25 == 0:

                    self.stdout.write(
                        f"{completed}/{total_products} products processed..."
                    )

        queue.put(None)

        queue.join()

        writer.join()

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("DOWNLOAD COMPLETE")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Images Saved : {writer.saved}")
        self.stdout.write(f"Failed       : {writer.failed}")
        self.stdout.write("=" * 70)