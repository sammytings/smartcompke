from abc import ABC, abstractmethod


class BaseScraper(ABC):

    @abstractmethod
    def scrape(self, url):
        """
        Returns a dictionary like:

        {
            "name": "",
            "brand": "",
            "category": "",
            "description": "",
            "short_description": "",
            "price": 0,
            "stock": 0,
            "images": [],
            "specifications": {},
            "variants": [],
        }
        """
        pass