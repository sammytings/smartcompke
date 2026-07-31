import logging
import threading

from django.core.files.base import ContentFile

from app.models import Product, ProductImage


logger = logging.getLogger(__name__)


class ImageWriter(threading.Thread):
    """
    Single database writer.

    Receives downloaded images from the queue
    and saves them safely to Django models.

    Only this thread touches the database.
    """


    def __init__(
        self,
        queue,
        total_images=None,
    ):

        super().__init__()

        self.queue = queue
        self.total_images = total_images

        self.saved = 0
        self.failed = 0

        self.running = True



    def run(self):

        while self.running:

            item = self.queue.get()


            # Stop signal
            if item is None:

                self.queue.task_done()

                break


            try:

                self.save_image(item)

                self.saved += 1


                if self.total_images:

                    print(
                        f"Images saved: "
                        f"{self.saved}/{self.total_images}"
                    )


            except Exception as e:

                self.failed += 1

                logger.exception(
                    "Failed saving image: %s",
                    e
                )


            finally:

                self.queue.task_done()



    def save_image(
        self,
        data
    ):

        product_id = data["product_id"]

        image_bytes = data["image"]

        filename = data["filename"]

        position = data["position"]



        product = Product.objects.get(
            id=product_id
        )


        # Prevent duplicate imports
        exists = ProductImage.objects.filter(
            product=product,
            image__icontains=filename
        ).exists()


        if exists:

            return



        image_file = ContentFile(
            image_bytes
        )


        is_primary = (
            position == 0
        )


        ProductImage.objects.create(

            product=product,

            image=(
                filename,
                image_file
            ),

            is_primary=is_primary,

        )