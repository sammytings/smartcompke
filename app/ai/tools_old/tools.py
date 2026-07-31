from django.db.models import Q
from app.models import Product


def find_products(question):

    words = question.split()

    query = Q()

    for word in words:

        query |= Q(name__icontains=word)

        query |= Q(description__icontains=word)


    products = Product.objects.filter(
        query
    ).distinct()[:8]


    return products