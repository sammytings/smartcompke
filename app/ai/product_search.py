from django.db.models import Q

from app.models import Product


def find_products(question):

    words = question.split()

    q = Q()

    for word in words:

        q |= Q(name__icontains=word)

        q |= Q(description__icontains=word)

    return Product.objects.filter(q)[:8]