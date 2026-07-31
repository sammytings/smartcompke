from django.utils.text import slugify

from app.models import Brand


class BrandDetector:

    KNOWN_BRANDS = [

        "HP",
        "Canon",
        "Epson",
        "Dell",
        "Lenovo",
        "Acer",
        "Asus",
        "Apple",
        "Samsung",
        "Brother",
        "Kyocera",
        "Ricoh",
        "Sharp",
        "MSI",
        "Huawei",
        "Logitech",
        "Kingston",
        "Sandisk",
        "Seagate",
        "Western Digital",
        "Crucial",
        "TP-Link",
        "D-Link",
        "Cisco",
        "Mikrotik",
        "Intel",
        "AMD",
        "NVIDIA",
    ]

    @classmethod
    def detect(cls, row):

        brand = row.get("Brands", "").strip()

        if brand:

            obj, _ = Brand.objects.get_or_create(

                name=brand,

                defaults={
                    "slug": slugify(brand)
                }
            )

            return obj

        # fallback using product name
        name = row.get("Name", "").lower()

        for item in cls.KNOWN_BRANDS:

            if item.lower() in name:

                obj, _ = Brand.objects.get_or_create(

                    name=item,

                    defaults={
                        "slug": slugify(item)
                    }
                )

                return obj

        return None