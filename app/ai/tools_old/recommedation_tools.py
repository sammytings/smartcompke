from .product_tools import search_products


def recommend_products(message):

    products = search_products(message)

    products["message"] = (

        "Based on your request, these are my recommendations."

    )

    return products