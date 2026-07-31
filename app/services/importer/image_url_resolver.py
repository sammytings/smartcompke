import re

import requests


class ImageURLResolver:
    """
    Converts WooCommerce thumbnail URLs into the
    highest-resolution image available.

    It tries multiple filename variants until one exists.
    """

    TIMEOUT = 15

    session = requests.Session()

    CANDIDATES = [

        # Original image
        lambda u: re.sub(
            r"-\d+x\d+(?=\.)",
            "",
            u,
        ),

        # Remove "-scaled"
        lambda u: u.replace(
            "-scaled",
            "",
        ),

        # HP
        lambda u: u.replace(
            "/lowres/",
            "/highres/",
        ),

        # WordPress
        lambda u: u.replace(
            "/thumbnail/",
            "/large/",
        ),

        lambda u: u.replace(
            "/medium/",
            "/large/",
        ),

        lambda u: u.replace(
            "/small/",
            "/large/",
        ),

        lambda u: u.replace(
            "/tiny/",
            "/large/",
        ),

        # Original uploads folder
        lambda u: re.sub(
            r"-\d+x\d+(?=\.)",
            "",
            u.replace(
                "/large/",
                "/",
            ),
        ),
    ]

    @classmethod
    def resolve(cls, url):

        tried = set()

        for fn in cls.CANDIDATES:

            candidate = fn(url)

            if candidate in tried:
                continue

            tried.add(candidate)

            if cls.exists(candidate):

                return candidate

        return url

    @classmethod
    def exists(cls, url):

        try:

            response = cls.session.head(

                url,

                allow_redirects=True,

                timeout=cls.TIMEOUT,
            )

            if response.status_code == 200:

                return True

        except Exception:

            pass

        return False