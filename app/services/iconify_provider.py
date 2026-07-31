import requests


class IconifyProvider:

    SEARCH_API = "https://api.iconify.design/search"

    @classmethod
    def search(cls, category_name):

        try:

            r = requests.get(
                cls.SEARCH_API,
                params={
                    "query": category_name,
                    "limit": 1,
                },
                timeout=20,
            )

            r.raise_for_status()

            data = r.json()

            if not data.get("icons"):
                return None

            icon = data["icons"][0]

            prefix, name = icon.split(":")

            icon_url = (
                f"https://api.iconify.design/{prefix}.json"
            )

            r = requests.get(
                icon_url,
                params={
                    "icons": name,
                },
                timeout=20,
            )

            r.raise_for_status()

            data = r.json()

            body = data["icons"][name]["body"]

            width = data.get("width", 24)
            height = data.get("height", 24)

            svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {width} {height}">
{body}
</svg>
"""

            return svg

        except Exception as e:

            print("Iconify Error:", e)

            return None