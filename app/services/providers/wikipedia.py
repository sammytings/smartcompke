import requests


class WikipediaProvider:

    API = "https://en.wikipedia.org/w/api.php"

    HEADERS = {
        "User-Agent": "SmartComputersKeBot/1.0"
    }

    @classmethod
    def search(cls, brand_name):
        """
        Returns Wikipedia page title if found.
        """

        params = {
            "action": "query",
            "list": "search",
            "format": "json",
            "srsearch": brand_name,
            "srlimit": 1,
        }

        try:
            r = requests.get(
                cls.API,
                params=params,
                headers=cls.HEADERS,
                timeout=15,
            )

            data = r.json()

            results = data["query"]["search"]

            if not results:
                return None

            return results[0]["title"]

        except Exception:
            return None

    @classmethod
    def get_logo(cls, page_title):
        """
        Returns image url from Wikipedia.
        """

        params = {
            "action": "query",
            "titles": page_title,
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
        }

        try:
            r = requests.get(
                cls.API,
                params=params,
                headers=cls.HEADERS,
                timeout=15,
            )

            pages = r.json()["query"]["pages"]

            page = next(iter(pages.values()))

            return page["original"]["source"]

        except Exception:
            return None