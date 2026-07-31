import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.db import close_old_connections

from app.models import Product
from .image_writer import ImageWriter


class ImageDownloader:

    MAX_THREADS = 10
    TIMEOUT = 30

    def __init__(self):

        self.downloaded = 0
        self.failed = 0
        self.skipped = 0

        self.total_products = 0
        self.total_images = 0

        self.lock = threading.Lock()

        # Queue consumed by ImageWriter
        self.queue = Queue(maxsize=200)

        self.writer = ImageWriter(self.queue)

        self.session = self.create_session()

    def create_session(self):
        """
        Creates a requests session with
        automatic retries and connection pooling.
        """

        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=1,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=retry,
        )

        session = requests.Session()

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            }
        )

        return session

    def run(self):

        products = Product.objects.exclude(
            wordpress_images=""
        ).exclude(
            wordpress_images__isnull=True
        )

        self.total_products = products.count()

        self.total_images = sum(
            len(
                [
                    x
                    for x in p.wordpress_images.splitlines()
                    if x.strip()
                ]
            )
            for p in products
        )

        print()
        print("=" * 70)
        print(f"{self.total_products} products")
        print(f"{self.total_images} images")
        print("=" * 70)
        print()

        # Start the database writer
        self.writer.start()

        close_old_connections()

        with ThreadPoolExecutor(
            max_workers=self.MAX_THREADS
        ) as executor:

            futures = []

            for product in products:

                futures.append(
                    executor.submit(
                        self.download_product,
                        product,
                    )
                )

            for future in as_completed(futures):

                try:
                    future.result()

                except Exception as e:
                    print(e)

        # Wait until all queued saves finish
        self.queue.join()

        self.writer.stop()
        self.queue.put(None)

        self.writer.join()

        self.summary()

    def download_product(self, product):
        """
        Download every image for a product.

        Download threads NEVER touch the database.
        They only download files and push them
        into the queue for ImageWriter.
        """

        urls = [
            url.strip()
            for url in product.wordpress_images.splitlines()
            if url.strip()
        ]

        if not urls:

            with self.lock:
                self.skipped += 1

            return

        success = False

        for index, url in enumerate(urls):

            try:

                self.download_image(
                    product,
                    url,
                    primary=(index == 0),
                )

                success = True

            except Exception as e:

                print()
                print(f"FAILED: {product.name}")
                print(url)
                print(e)

        with self.lock:

            if success:
                self.downloaded += 1
            else:
                self.failed += 1
            self.print_progress()

    def download_image(
        self,
        product,
        url,
        primary=False,
    ):
        """
        Downloads ONE image and places it
        into the writer queue.
        """

        response = self.session.get(
            url,
            timeout=self.TIMEOUT,
            stream=True,
        )

        response.raise_for_status()

        suffix = os.path.splitext(url)[1]

        if not suffix:
            suffix = ".jpg"

        temp = tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        )

        for chunk in response.iter_content(8192):

            if chunk:
                temp.write(chunk)

        temp.seek(0)

        filename = os.path.basename(url)

        self.queue.put(
            {
                "product": product,
                "temp_file": temp,
                "filename": filename,
                "primary": primary,
            }
        )


    def print_progress(self):
        """
        Display current download progress.
        """

        completed = self.downloaded + self.failed + self.skipped

        if self.total_products == 0:
            return

        percent = (completed / self.total_products) * 100

        print(
            f"\rProcessed: {completed}/{self.total_products} "
            f"({percent:.1f}%) | "
            f"Downloaded: {self.downloaded} | "
            f"Skipped: {self.skipped} | "
            f"Failed: {self.failed}",
            end="",
            flush=True,
        )

    def summary(self):

        print()
        print()
        print("=" * 70)
        print("DOWNLOAD COMPLETE")
        print("=" * 70)

        print(f"Products          : {self.total_products}")
        print(f"Images            : {self.total_images}")

        print()

        print(f"Downloaded        : {self.downloaded}")
        print(f"Skipped           : {self.skipped}")
        print(f"Failed            : {self.failed}")

        print()

        print(f"Images Saved      : {self.writer.saved}")
        print(f"Database Failures : {self.writer.failed}")

        print("=" * 70)