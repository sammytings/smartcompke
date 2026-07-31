from abc import ABC, abstractmethod


class BaseImporter(ABC):

    supported_domains = []

    @abstractmethod
    def import_product(self, url):
        """
        Returns an ImportedProduct object.
        """
        pass