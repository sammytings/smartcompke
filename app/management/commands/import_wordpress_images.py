from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from app.services.image_importer import ImageImporter


class Command(BaseCommand):

    help = "Import WordPress images into Django products"

    def add_arguments(self, parser):

        parser.add_argument(
            "--media",
            type=str,
            default=str(Path(settings.BASE_DIR) / "media"),
            help="Folder containing the extracted WordPress uploads",
        )

        parser.add_argument(
            "--csv",
            type=str,
            default=r"C:\Users\user\Downloads\wc-product-export-29-7-2026-1785330184424.csv",
            help="WooCommerce CSV export",
        )

    def handle(self, *args, **options):

        media_folder = options["media"]
        csv_file = options["csv"]

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("SMART WORDPRESS IMAGE IMPORTER")
        self.stdout.write("=" * 70)

        importer = ImageImporter(
            media_folder=media_folder,
            csv_file=csv_file,
        )

        importer.run()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Finished importing images."))