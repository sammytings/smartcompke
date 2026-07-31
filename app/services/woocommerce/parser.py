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

                if row.get("Type") == "variation":
                    continue

                yield row