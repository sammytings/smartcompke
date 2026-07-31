import tempfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .image_optimizer import ImageOptimizer
from .image_url_resolver import ImageURLResolver
from .image_validator import ImageValidator


class ImageDownloader:

    TIMEOUT = 60

    def __init__(self):

        self.session = requests.Session()

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
            pool_connections=100,
            pool_maxsize=100,
            max_retries=retry,
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({

            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36"
                " Chrome/138.0 Safari/537.36"

        })

    def download_product(self, product):

        jobs = []

        if not product.wordpress_images:
            return jobs

        urls = []

        seen = set()

        for url in product.wordpress_images.splitlines():

            url = url.strip()

            if not url:
                continue

            url = ImageURLResolver.resolve(url)

            if url in seen:
                continue

            seen.add(url)

            urls.append(url)

        for index, url in enumerate(urls):

            try:

                file = self.download(url)

                if not ImageValidator.validate(file):

                    file.close()

                    print(
                        f"INVALID IMAGE: {product.name}"
                    )

                    continue

                if ImageValidator.duplicate(file):

                    file.close()

                    continue

                file = ImageOptimizer.optimize(file)

                jobs.append({

                    "product": product,

                    "temp_file": file,

                    "filename": url.split("/")[-1],

                    "primary": index == 0,

                })

            except Exception as e:

                print()
                print("=" * 70)
                print(product.name)
                print(url)
                print(e)
                print("=" * 70)

        return jobs

    def download(self, url):

        response = self.session.get(

            url,

            timeout=self.TIMEOUT,

            stream=True,

        )

        response.raise_for_status()

        temp = tempfile.NamedTemporaryFile()

        for chunk in response.iter_content(1024 * 128):

            if chunk:

                temp.write(chunk)

        temp.seek(0)

        return temp