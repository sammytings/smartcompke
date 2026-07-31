from django.db import transaction

from .parser import WooCommerceParser
from .product_importer import ProductImporter


class WooCommerceImporter:

    def __init__(self, csv_file):

        self.parser = WooCommerceParser(csv_file)

        self.imported = 0
        self.updated = 0
        self.failed = 0

    @transaction.atomic
    def run(self):

        rows = list(self.parser.rows())

        total = len(rows)

        print()
        print("=" * 70)
        print(f"{total} products found")
        print("=" * 70)
        print()

        for index, row in enumerate(rows, start=1):

            name = row.get("Name", "Unknown")

            print(f"[{index}/{total}] {name}")

            try:

                created = self.import_product(row)

                if created:

                    self.imported += 1
                    print("   ✓ Imported")

                else:

                    self.updated += 1
                    print("   ↺ Updated")

            except Exception as e:

                self.failed += 1

                print(f"   ✗ {e}")

        self.summary()

    def import_product(self, row):

        slug = ProductImporter.import_product(row)

        return slug

    def summary(self):

        print()
        print("=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"Imported : {self.imported}")
        print(f"Updated  : {self.updated}")
        print(f"Failed   : {self.failed}")
        print("=" * 70)