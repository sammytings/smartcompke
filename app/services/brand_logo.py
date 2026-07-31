from django.core.files.base import ContentFile

from app.services.image_fetcher import ImageFetcher
from app.services.providers.wikimedia import WikimediaProvider


class BrandLogoService:

    @classmethod
    def fetch(cls, brand):

        print("=" * 60)
        print("BrandLogoService started")
        print("=" * 60)

        # Skip if logo already exists
        if brand.logo:
            print("Brand already has a logo.")
            return

        print(f"Searching Wikimedia for '{brand.name}'...")

        logo_url = WikimediaProvider.search(brand.name)

        print("Logo URL =", logo_url)

        if not logo_url:
            print("No logo found.")
            return

        image = ImageFetcher.download(logo_url)

        print("Image downloaded =", image is not None)

        if not image:
            print("Download failed.")
            return

        brand.logo.save(
            f"{brand.name.lower().replace(' ', '_')}.png",
            ContentFile(image),
            save=True,
        )

        print("SUCCESS! Logo saved.")