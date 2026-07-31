import os
import uuid

import requests

from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ImageService:

    HEADERS = {

        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),

        "Accept": (
            "image/avif,image/webp,image/apng,image/svg+xml,"
            "image/*,*/*;q=0.8"
        ),

        "Accept-Language": "en-US,en;q=0.9",

        "Referer": "https://www.google.com/",

        "Connection": "keep-alive",

    }

    ALLOWED_EXTENSIONS = (

        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".avif",

    )

    # -------------------------------------------------------

    @classmethod
    def is_valid_image_url(cls, url):

        if not url:
            return False

        url = url.lower()

        if url.startswith("//"):
            return True

        if url.startswith("http://"):
            return True

        if url.startswith("https://"):
            return True

        return False

    # -------------------------------------------------------

    @classmethod
    def normalize_url(cls, url):

        if not url:
            return None

        url = url.strip()

        if url.startswith("//"):
            url = "https:" + url

        return url

    # -------------------------------------------------------

    @classmethod
    def download_bytes(cls, url):

        url = cls.normalize_url(url)

        if not cls.is_valid_image_url(url):
            return None

        last_error = None

        for attempt in range(3):

            try:

                response = requests.get(

                    url,

                    headers=cls.HEADERS,

                    timeout=30,

                    allow_redirects=True,

                    stream=True,

                )

                response.raise_for_status()

                return response.content

            except Exception as e:

                last_error = e

        print("IMAGE DOWNLOAD FAILED:", last_error)

        return None

    # -------------------------------------------------------

    @classmethod
    def convert_to_webp(cls, image_bytes):

        image = Image.open(
            BytesIO(image_bytes)
        )

        if image.mode in ("RGBA", "P"):

            image = image.convert("RGB")

        elif image.mode != "RGB":

            image = image.convert("RGB")

        filename = f"{uuid.uuid4()}.webp"

        path = os.path.join(

            "products",

            filename,

        )

        output = BytesIO()

        image.save(

            output,

            format="WEBP",

            quality=90,

            optimize=True,

            method=6,

        )

        default_storage.save(

            path,

            ContentFile(output.getvalue())

        )

        return path

    # -------------------------------------------------------

    @classmethod
    def download_image(cls, url):

        try:

            data = cls.download_bytes(url)

            if not data:
                return None

            return cls.convert_to_webp(data)

        except Exception as e:

            print("IMAGE ERROR:", e)

            return None

    # -------------------------------------------------------

    @classmethod
    def download_gallery(cls, images):

        saved = []

        seen = set()

        for image in images:

            if isinstance(image, dict):

                image = (

                    image.get("contentUrl")

                    or image.get("url")

                    or image.get("src")

                )

            if not image:
                continue

            image = cls.normalize_url(image)

            if not image:
                continue

            if image in seen:
                continue

            seen.add(image)

            try:

                path = cls.download_image(image)

                if path:

                    saved.append(path)

            except Exception as e:

                print(e)

        return saved

    # -------------------------------------------------------

    @classmethod
    def first