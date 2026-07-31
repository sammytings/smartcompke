import requests
from django.conf import settings


class BraveProvider:

    API = "https://api.search.brave.com/res/v1/images/search"

    HEADERS = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY,
    }

    @classmethod
    def search(cls, brand_name):

        query = f"{brand_name} official logo png transparent"

        params = {
            "q": query,
            "count": 10,
        }

        r = requests.get(
            cls.API,
            headers=cls.HEADERS,
            params=params,
            timeout=20,
        )

        r.raise_for_status()

        return r.json()