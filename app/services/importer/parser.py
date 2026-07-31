import csv
import sys

csv.field_size_limit(sys.maxsize)


class WooCommerceParser:

    def __init__(self, csv_file):
        self.csv_file = csv_file

    def rows(self):

        with open(
            self.csv_file,
            newline="",
            encoding="utf-8-sig",
            errors="ignore",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                # Ignore empty rows
                if not row:
                    continue

                # Ignore product variations
                if row.get("Type", "").lower() == "variation":
                    continue

                # Ignore drafts/private products
                published = row.get("Published", "1").strip().lower()

                if published in (
                    "0",
                    "false",
                    "no",
                    "draft",
                    "private",
                ):
                    continue

                # Clean values
                cleaned = {}

                for key, value in row.items():

                    if key is None:
                        continue

                    key = key.strip()

                    if value is None:
                        cleaned[key] = ""
                    else:
                        cleaned[key] = str(value).strip()

                yield cleaned