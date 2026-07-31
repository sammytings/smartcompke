import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)


class CSVImageMapper:

    def __init__(self, csv_file):

        self.csv_file = Path(csv_file)
        self.products = {}

    def build(self):

        self.products.clear()

        with open(
            self.csv_file,
            newline="",
            encoding="utf-8-sig",
            errors="ignore",
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                name = row.get("Name", "").strip()

                images = row.get("Images", "").strip()

                if not name or not images:
                    continue

                first_image = images.split(",")[0].strip()

                filename = Path(first_image).name

                self.products[name.lower()] = filename

        return self.products

    def get_filename(self, product):

        return self.products.get(product.name.lower())