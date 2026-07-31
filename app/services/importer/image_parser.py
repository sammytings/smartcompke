import re


class ImageParser:
    """
    Extracts and normalizes WooCommerce image URLs.
    """

    @classmethod
    def urls(cls, product):

        if not product.wordpress_images:
            return []

        urls = []

        seen = set()

        for line in product.wordpress_images.splitlines():

            url = line.strip()

            if not url:
                continue

            url = cls.high_resolution(url)

            if url in seen:
                continue

            seen.add(url)

            urls.append(url)

        return urls

    @staticmethod
    def high_resolution(url):

        # WooCommerce thumbnail
        url = re.sub(
            r"-\d+x\d+(?=\.)",
            "",
            url,
        )

        # HP
        url = url.replace(
            "/lowres/",
            "/highres/",
        )

        # Wordpress thumbnails
        url = url.replace(
            "/thumbnail/",
            "/large/",
        )

        url = url.replace(
            "/tiny/",
            "/large/",
        )

        url = url.replace(
            "/medium/",
            "/large/",
        )

        url = url.replace(
            "/small/",
            "/large/",
        )

        return url

    @staticmethod
    def filename(url):

        return url.split("/")[-1].split("?")[0]