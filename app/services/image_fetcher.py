import os
import uuid
import requests

from io import BytesIO

from PIL import Image


from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ImageFetcher:

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
        )
    }

    TIMEOUT = 20

    @classmethod
    def download(cls, url):

        try:

            response = requests.get(
                url,
                headers=cls.HEADERS,
                timeout=cls.TIMEOUT,
            )

            if response.status_code != 200:
                return None

            content = response.content

          
            # ===========================
            # PNG / JPG / WEBP
            # ===========================

            image = Image.open(BytesIO(content))

            image.verify()

            return content

        except Exception as e:

            print(e)

            return None

    @classmethod
    def save_image(cls, image_bytes, folder, filename):

        extension = "png"

        path = os.path.join(
            folder,
            f"{filename}_{uuid.uuid4().hex[:8]}.{extension}",
        )

        default_storage.save(
            path,
            ContentFile(image_bytes),
        )

        return path