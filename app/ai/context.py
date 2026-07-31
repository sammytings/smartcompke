def business_context():

    return """
Store:
SmartComputersKE Technologies

We sell:

• Laptops
• Desktops
• Printers
• CCTV
• Accessories
• Networking
• Gaming
• Repairs

We deliver across Kenya.

We provide warranties where applicable.

If product information is supplied by the system,
use that instead of assumptions.
"""

from app.models import Product


def product_context(products):

    if not products:

        return "No products found."

    text = ""

    for p in products:

        text += f"""

Product

Name: {p.name}

Price: {p.current_price}

Description:

{p.description}

"""

    return text