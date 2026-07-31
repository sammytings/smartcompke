import os
import uuid

import requests

from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ImageService:


    HEADERS = {

        "User-Agent":
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/138 Safari/537.36"
        ),

        "Accept":
        "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",

    }


    MAX_SIZE = 10 * 1024 * 1024



    @classmethod
    def normalize_url(cls, url):

        if not url:
            return None


        url = url.strip()


        if url.startswith("//"):

            url = "https:" + url


        return url



    @classmethod
    def download_bytes(cls, url):

        url = cls.normalize_url(url)

        if not url:
            return None


        try:

            response = requests.get(

                url,

                headers=cls.HEADERS,

                timeout=25,

                stream=True

            )


            response.raise_for_status()


            content_type = response.headers.get(
                "Content-Type",
                ""
            )


            if "image" not in content_type:

                print(
                    "NOT IMAGE:",
                    content_type
                )

                return None



            size = 0
            data = BytesIO()


            for chunk in response.iter_content(1024):

                size += len(chunk)


                if size > cls.MAX_SIZE:

                    print(
                        "IMAGE TOO LARGE"
                    )

                    return None


                data.write(chunk)


            return data.getvalue()



        except Exception as e:


            print(
                "DOWNLOAD ERROR:",
                e
            )


            return None




    @classmethod
    def convert_to_webp(cls, image_bytes):

        try:


            image = Image.open(
                BytesIO(image_bytes)
            )


            if image.mode != "RGB":

                image = image.convert(
                    "RGB"
                )


            filename = (
                f"{uuid.uuid4()}.webp"
            )


            path = os.path.join(

                "products",

                filename

            )


            output = BytesIO()


            image.save(

                output,

                format="WEBP",

                quality=90,

                optimize=True

            )


            default_storage.save(

                path,

                ContentFile(
                    output.getvalue()
                )

            )


            return path



        except Exception as e:


            print(
                "CONVERSION ERROR:",
                e
            )


            return None





    @classmethod
    def download_image(cls, url):

        data = cls.download_bytes(url)


        if not data:

            return None


        return cls.convert_to_webp(
            data
        )




    @classmethod
    def download_gallery(cls, images, limit=8):

        saved = []

        seen = set()


        for image in images:


            if len(saved) >= limit:

                break



            if isinstance(image, dict):

                image = (

                    image.get("contentUrl")

                    or image.get("url")

                    or image.get("src")

                )


            image = cls.normalize_url(
                image
            )


            if not image:

                continue



            if image in seen:

                continue



            seen.add(image)



            path = cls.download_image(
                image
            )


            if path:

                saved.append(path)



        return saved