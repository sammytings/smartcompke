import json


class JsonLDParser:

    @staticmethod
    def extract(soup):

        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            try:

                data = json.loads(script.string)

            except Exception:
                continue

            if isinstance(data, list):

                for item in data:

                    if item.get("@type") == "Product":

                        return item

            elif isinstance(data, dict):

                if data.get("@type") == "Product":

                    return data

        return None