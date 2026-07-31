from django.utils.text import slugify

from app.models import Brand


class BrandDetector:

    BRAND_FIELDS = [
        "Brands",
        "Brand",
        "brand",
        "brands",
    ]

    COMMON_BRANDS = [
        "Apple",
        "HP",
        "Dell",
        "Lenovo",
        "Asus",
        "Acer",
        "Microsoft",
        "Canon",
        "Epson",
        "Samsung",
        "LG",
        "Intel",
        "AMD",
        "Kingston",
        "SanDisk",
        "Transcend",
        "Logitech",
        "TP-Link",
        "Mercusys",
        "Ugreen",
        "Anker",
        "Oraimo",
        "JBL",
        "Sony",
        "Huawei",
        "Xiaomi",
        "Infinix",
        "Tecno",
        "Realme",
        "Redmi",
        "MSI",
        "Razer",
        "Gigabyte",
        "Corsair",
        "AOC",
        "ViewSonic",
        "Brother",
        "Pantum",
        "D-Link",
        "Toshiba",
        "Seagate",
        "Western Digital",
        "WD",
        "Crucial",
        "Lexar",
        "HyperX",
        "Cisco",
        "MikroTik",
        "Hikvision",
        "Dahua",
        "ZKTeco",
        "APC",
        "Eaton",
        "Synology",
        "QNAP",
    ]

    @classmethod
    def detect(cls, row):

        # First check explicit brand columns
        for field in cls.BRAND_FIELDS:

            value = row.get(field, "").strip()

            if value:

                return cls.get_brand(value)

        # Otherwise detect from product name
        name = row.get("Name", "").strip()

        lower = name.lower()

        for brand in cls.COMMON_BRANDS:

            if lower.startswith(brand.lower() + " "):
                return cls.get_brand(brand)

            if f" {brand.lower()} " in f" {lower} ":
                return cls.get_brand(brand)

        return None

    @staticmethod
    def get_brand(name):

        name = name.strip()

        if not name:
            return None

        brand, _ = Brand.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
            },
        )

        return brand