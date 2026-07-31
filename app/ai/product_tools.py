from django.db.models import Q
from app.models import Product


def search(message):
    words = message.split()

    query = Q()

    for word in words:
        query |= Q(name__icontains=word)
        query |= Q(description__icontains=word)

    qs = Product.objects.filter(query).distinct()[:6]

    products = []

    for product in qs:
        image = ""

        if hasattr(product, "primary_image") and product.primary_image:
            image = product.primary_image.image.url

        products.append({
            "id": product.id,
            "name": product.name,
            "price": str(product.current_price),
            "url": product.get_absolute_url(),
            "image": image,
        })

    return products