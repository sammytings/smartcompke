from urllib.parse import urlparse

from .registry import get_importer

from .generic import GenericImporter

from .hp import HPImporter

from .dell import DellImporter

from .lenovo import LenovoImporter

from .asus import AsusImporter

from .registry import register


register(HPImporter)

register(DellImporter)

register(LenovoImporter)

register(AsusImporter)


class ImportManager:

    def import_product(self, url):

        domain = urlparse(url).netloc

        importer = get_importer(domain)

        if importer:

            return importer.import_product(url)

        return GenericImporter().import_product(url)