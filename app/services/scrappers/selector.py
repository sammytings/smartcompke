from urllib.parse import urlparse

from .jumia import JumiaScraper
from .gadgetsoko import GadgetSokoScraper
from .kilimall import KilimallScraper
from .phoneplace import PhonePlaceScraper
from .avechi import AvechiScraper


class ScraperSelector:

    @staticmethod
    def get_scraper(url):

        domain = urlparse(url).netloc.lower()

        if "jumia" in domain:
            return JumiaScraper()

        elif "gadgetsoko" in domain:
            return GadgetSokoScraper()

        elif "kilimall" in domain:
            return KilimallScraper()

        elif "phoneplace" in domain:
            return PhonePlaceScraper()

        elif "avechi" in domain:
            return AvechiScraper()

        raise Exception("Unsupported website")