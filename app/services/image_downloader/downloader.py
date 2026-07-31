from concurrent.futures import ThreadPoolExecutor, wait

from .worker import ImageWorker


class ImageDownloader:
    """
    Coordinates image download workers.

    Does not write to database.
    """

    def __init__(
        self,
        products,
        queue,
        workers=10,
    ):
        self.products = list(products)
        self.queue = queue
        self.workers = workers


    def run(self):

        with ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:

            futures = []


            for product in self.products:

                worker = ImageWorker(
                    product=product,
                    queue=self.queue,
                )


                futures.append(
                    executor.submit(
                        worker.run
                    )
                )


            wait(futures)