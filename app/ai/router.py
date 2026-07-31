from .intent import detect, Intent
from .responses import text, products, error
from .tools.product_tools import search


def route(request, message):
    """
    Main Smart AI router.
    """

    try:

        intent = detect(message)

        # Greeting
        if intent == Intent.GREETING:
            return text(
                "👋 Hello! I'm Smart AI. How can I help you today?"
            )

        # Product Search
        elif intent == Intent.PRODUCT:

            items = search(message)

            if items:

                return products(
                    "I found these products for you.",
                    items
                )

            return text(
                "Sorry, I couldn't find any matching products."
            )

        # Order Tracking
        elif intent == Intent.ORDER:

            return text(
                "📦 Order tracking is coming soon."
            )

        # Repairs
        elif intent == Intent.REPAIR:

            return text(
                "🛠 Repair assistance is coming soon."
            )

        return text(
            "I'm still learning. Please ask about products, orders or repairs."
        )

    except Exception as e:

        return error(str(e))