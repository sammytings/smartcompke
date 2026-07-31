import requests

from urllib.parse import urlparse
from pathlib import Path

from django.core.files import File
from django.db import transaction

from app.models import Product
from app.services.image_indexer import ImageIndexer
from app.services.image_matcher import ImageMatcher
from .parsers.generic import GenericParser
from app.services.csv_image_mapper import CSVImageMapper

def import_product_data(url):

    domain = urlparse(url).netloc.lower()

    if "hp.com" in domain:
        parser = GenericParser()

    elif "lenovo.com" in domain:
        parser = GenericParser()

    elif "dell.com" in domain:
        parser = GenericParser()

    elif "asus.com" in domain:
        parser = GenericParser()

    else:
        parser = GenericParser()

    return parser.parse(url)