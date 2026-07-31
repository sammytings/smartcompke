IMPORTERS = []


def register(importer):

    IMPORTERS.append(importer)


def get_importer(domain):

    for importer in IMPORTERS:

        if domain in importer.supported_domains:

            return importer()

    return None