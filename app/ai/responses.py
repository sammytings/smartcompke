def text(message):

    return {
        "type": "text",
        "message": message
    }


def products(message, products):

    return {
        "type": "products",
        "message": message,
        "products": products
    }


def error(message):

    return {
        "type": "error",
        "message": message
    }