from .base import BaseScraper


class JumiaScraper(BaseScraper):

    def scrape(self, url):

        return {
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