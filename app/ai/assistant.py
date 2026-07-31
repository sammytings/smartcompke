from .grok import GrokClient

from .tools import find_products

from .context import product_context


class SmartAI:

    def __init__(self, request):

        self.request = request

        self.grok = GrokClient()

    def reply(self, message):

        products = find_products(message)

        context = product_context(products)

        response = self.grok.chat(

            user_message=message,

            context=context

        )

        return {

            "type": "text",

            "message": response["message"]

        }