import requests


class WikimediaProvider:

    API = "https://commons.wikimedia.org/w/api.php"

    HEADERS = {
        "User-Agent": "SmartComputersKe/1.0"
    }

    @classmethod
    def search(cls, brand_name):
        """
        Search Wikimedia Commons specifically for logo files.
        """

        queries = [
            f"{brand_name} logo png",
            f"{brand_name} official logo png",
            f"{brand_name} logo transparent png",
        ]

        for query in queries:

            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,   # File namespace only
                "gsrlimit": 10,

                "prop": "imageinfo",
                "iiprop": "url",

                "format": "json",
            }

            try:

                r = requests.get(
                    cls.API,
                    params=params,
                    headers=cls.HEADERS,
                    timeout=20,
                )

                r.raise_for_status()

                data = r.json()

                if "query" not in data:
                    continue

                pages = data["query"].get("pages", {})

                if not pages:
                    continue

                return cls._pick_best(pages, brand_name)

            except Exception as e:

                print(e)

        return None
    @classmethod
    def _pick_best(cls, pages, brand_name):

        best_score = -1
        best_url = None

        brand_name = brand_name.lower()

        BAD_WORDS = [
        "ux",
        "linux",
        "software",
        "printer",
        "driver",
        "icon",
        "badge",
        "old",
        "legacy",
        "product",
        "operating",
        "system",
    ]

        for page in pages.values():

            title = page.get("title", "").lower()

            imageinfo = page.get("imageinfo")

            if not imageinfo:
                continue

            url = imageinfo[0]["url"]

        # Ignore SVG files for now
            if url.lower().endswith(".svg"):
                continue

            score = 0

        # Exact brand match
            if brand_name in title:
                score += 100

        # Prefer logo files
            if "logo" in title:
                score += 60

        # Prefer PNG
            if url.lower().endswith(".png"):
                score += 40

        # Penalize unrelated files
            for word in BAD_WORDS:
                if word in title:
                    score -= 100

            print(f"{title} -> {score}")

            if score > best_score:
                best_score = score
                best_url = url

        return best_url