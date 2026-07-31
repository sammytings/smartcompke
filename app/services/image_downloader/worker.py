import requests
import time
import logging

from urllib.parse import urlparse

from django.conf import settings


logger = logging.getLogger(__name__)


class ImageWorker:
    """
    Downloads images for a single product.

    Responsibilities:
    - extract image URLs
    - download original images
    - retry failed downloads
    - send completed images to ImageWriter queue

    Does NOT touch the database.
    """


    MAX_RETRIES = 3
    TIMEOUT = 30


    def __init__(
        self,
        product,
        queue,
    ):

        self.product = product
        self.queue = queue



    def run(self):

        images = self.get_product_images()


        for index, image_url in enumerate(images):

            result = self.download_image(
                image_url=image_url,
                position=index,
            )


            if result:

                self.queue.put(result)





    def get_product_images(self):

        """
        Collect product image URLs.

        Supports:
        - Product.image
        - ProductImage gallery
        """

        urls = []


        # Main image
        image = getattr(
            self.product,
            "image",
            None
        )


        if image:

            if image.name:

                urls.append(
                    image.url
                )



        # Gallery images
        if hasattr(
            self.product,
            "images"
        ):

            for image in self.product.images.all():

                if image.image:

                    urls.append(
                        image.image.url
                    )



        # remove duplicates
        return list(
            dict.fromkeys(urls)
        )





    def normalize_url(
        self,
        image_url
    ):

        """
        Converts Django media paths into
        complete URLs.
        """

        if not image_url:

            return None



        # Already a complete URL
        if image_url.startswith(
            "http://"
        ) or image_url.startswith(
            "https://"
        ):

            return image_url



        # Django media path
        if image_url.startswith(
            "/media/"
        ):


            base_url = getattr(
                settings,
                "SITE_URL",
                "http://127.0.0.1:8000"
            )


            return (
                base_url.rstrip("/")
                +
                image_url
            )



        return None





    def download_image(
        self,
        image_url,
        position=0,
    ):

        """
        Download one image.

        Returns data for ImageWriter.
        """

        image_url = self.normalize_url(
            image_url
        )


        if not image_url:

            logger.warning(
                "Skipping invalid image URL"
            )

            return None



        for attempt in range(
            1,
            self.MAX_RETRIES + 1
        ):


            try:

                response = requests.get(

                    image_url,

                    timeout=self.TIMEOUT,

                    headers={
                        "User-Agent":
                        (
                            "Mozilla/5.0 "
                            "(Windows NT 10.0; Win64; x64)"
                        )
                    }

                )



                if response.status_code != 200:

                    raise Exception(
                        f"HTTP {response.status_code}"
                    )



                filename = self.generate_filename(
                    image_url
                )



                return {

                    "product_id":
                        self.product.id,


                    "image":
                        response.content,


                    "filename":
                        filename,


                    "position":
                        position,


                    "url":
                        image_url,

                }



            except Exception as e:


                logger.warning(

                    "Image failed %s attempt %s/%s : %s",

                    image_url,

                    attempt,

                    self.MAX_RETRIES,

                    e

                )



                time.sleep(
                    attempt * 2
                )



        logger.error(
            "Giving up on image %s",
            image_url
        )


        return None





    def generate_filename(
        self,
        url
    ):


        path = urlparse(url).path


        filename = path.split("/")[-1]



        if not filename:


            filename = (
                f"image_{int(time.time())}.jpg"
            )



        return filename