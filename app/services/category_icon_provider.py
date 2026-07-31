import requests


class CategoryIconProvider:
    """
    Searches Wikimedia Commons for category icons.
    """

    API = "https://commons.wikimedia.org/w/api.php"

    HEADERS = {
        "User-Agent": "SmartComputersKe/1.0 (https://smartcomputerske.co.ke)"
    }

    @classmethod
    def search(cls, category_name):

        queries = [
            f"{category_name} icon",
            f"{category_name} logo",
            f"{category_name} symbol",
            category_name,
        ]

        for query in queries:

            print(f"Searching Wikimedia for: {query}")

            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,
                "gsrlimit": 10,
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json",
            }

            try:
                response = requests.get(
                    cls.API,
                    params=params,
                    headers=cls.HEADERS,
                    timeout=20,
                )

                response.raise_for_status()

                data = response.json()

                pages = data.get("query", {}).get("pages", {})

                for page in pages.values():

                    imageinfo = page.get("imageinfo")

                    if not imageinfo:
                        continue

                    url = imageinfo[0].get("url")

                    if not url:
                        continue

                    lower = url.lower()

                    if lower.endswith((".png", ".svg", ".jpg", ".jpeg")):
                        print("Found:", url)
                        return url

            except Exception as e:
                print("Provider Error:", e)

        print("No icon found.")
        return None