from django.utils.text import slugify
from app.models import Product, ProductVariant
import uuid


from django.utils.text import slugify
from app.models import Product, ProductVariant
import uuid

from django.utils.text import slugify
from app.models import Product

MAX_SLUG_LENGTH = 100


def generate_unique_slug(name):
    base_slug = slugify(name) or "product"

    base_slug = base_slug[:MAX_SLUG_LENGTH].rstrip("-")

    slug = base_slug
    counter = 1

    while Product.objects.filter(slug=slug).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[:MAX_SLUG_LENGTH-len(suffix)]}{suffix}"
        counter += 1

    return slug



def generate_unique_sku(sku=None):
    """
    Generate a unique SKU for product variants.
    """

    if not sku:

        sku = f"IMP-{uuid.uuid4().hex[:8].upper()}"


    original_sku = sku

    counter = 1


    while ProductVariant.objects.filter(sku=sku).exists():

        sku = f"{original_sku}-{counter}"

        counter += 1


    return sku




def safe_text(value):
    """
    Returns a cleaned string.
    """

    if value is None:

        return ""


    return str(value).strip()




def first_not_empty(*values):
    """
    Returns the first non-empty value.
    """

    for value in values:

        if value:

            value = str(value).strip()

            if value:

                return value


    return ""