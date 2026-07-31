from django.core.management.base import BaseCommand

from app.services.importer.importer import WooCommerceImporter


class Command(BaseCommand):
    help = "Import WooCommerce products"

    def add_arguments(self, parser):

        parser.add_argument(
            "csv_file",
            type=str,
            help="WooCommerce CSV export",
        )

    def handle(self, *args, **options):

        importer = WooCommerceImporter(

            options["csv_file"]

        )

        importer.run()