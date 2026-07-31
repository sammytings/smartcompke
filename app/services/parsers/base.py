import json
import re
import requests

from bs4 import BeautifulSoup


class BaseParser:
    """
    Base parser inherited by all website parsers.

    Features
    --------
    ✔ Browser-like headers
    ✔ Automatic retries
    ✔ BeautifulSoup
    ✔ JSON-LD extraction
    ✔ OpenGraph extraction
    ✔ Helpers
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    TIMEOUT = 30

    def __init__(self, url):
        self.url = url

    # --------------------------------------------------

    def get_response(self):

        last_error = None

        for _ in range(3):

            try:

                response = requests.get(
                    self.url,
                    headers=self.HEADERS,
                    timeout=self.TIMEOUT,
                )

                response.raise_for_status()

                return response

            except Exception as e:
                last_error = e

        raise Exception(last_error)

    # --------------------------------------------------

    def get_soup(self):

        response = self.get_response()

        return BeautifulSoup(
            response.text,
            "lxml",
        )

    # --------------------------------------------------

    def get_json_ld(self, soup):

        scripts = soup.find_all(
            "script",
            type="application/ld+json",
        )

        for script in scripts:

            try:

                text = script.string

                if not text:
                    text = script.text

                if not text:
                    continue

                obj = json.loads(text)

                if isinstance(obj, dict):

                    if "@graph" in obj:

                        for item in obj["@graph"]:

                            if (
                                isinstance(item, dict)
                                and item.get("@type") == "Product"
                            ):
                                return item

                    elif obj.get("@type") == "Product":
                        return obj

            except Exception:
                pass

        return None

    # --------------------------------------------------

    def get_meta(self, soup, prop):

        tag = soup.find(
            "meta",
            attrs={"property": prop},
        )

        if tag:
            return tag.get("content", "").strip()

        tag = soup.find(
            "meta",
            attrs={"name": prop},
        )

        if tag:
            return tag.get("content", "").strip()

        return ""

    # --------------------------------------------------

    def clean_price(self, value):

        if value is None:
            return "0"

        value = str(value)

        value = value.replace(",", "")

        match = re.search(
            r"[\d.]+",
            value,
        )

        if match:
            return match.group()

        return "0"

    # --------------------------------------------------

    def absolute_image(self, url):

        if not url:
            return ""

        if url.startswith("//"):
            return "https:" + url

        return url

    # --------------------------------------------------

    def extract_images_from_jsonld(self, product):

        images = []

        image = product.get("image")

        if isinstance(image, list):

            for img in image:

                if isinstance(img, str):
                    images.append(
                        self.absolute_image(img)
                    )

                elif isinstance(img, dict):

                    url = (
                        img.get("contentUrl")
                        or img.get("url")
                    )

                    if url:
                        images.append(
                            self.absolute_image(url)
                        )

        elif isinstance(image, dict):

            urls = (
                image.get("contentUrl")
                or image.get("url")
            )

            if isinstance(urls, list):

                for u in urls:
                    images.append(
                        self.absolute_image(u)
                    )

            elif urls:
                images.append(
                    self.absolute_image(urls)
                )

        elif isinstance(image, str):

            images.append(
                self.absolute_image(image)
            )

        # remove duplicates

        unique = []

        for img in images:

            if img not in unique:
                unique.append(img)

        return unique

    # --------------------------------------------------

    def extract_og_images(self, soup):

        images = []

        for tag in soup.find_all(
            "meta",
            attrs={"property": "og:image"},
        ):

            url = tag.get("content")

            if url:
                images.append(
                    self.absolute_image(url)
                )

        return images

    # --------------------------------------------------

    def parse(self):
        raise NotImplementedError