class ContentGenerator:

    @staticmethod
    def generate(product):

        if not product.short_description:

            product.short_description = (
                f"{product.name} from {product.brand}. "
                "High-quality genuine product available at SmartComputersKE."
            )

        if not product.seo_title:

            product.seo_title = (
                f"{product.name} | Buy Online in Kenya"
            )

        if not product.meta_description:

            product.meta_description = (
                f"Buy {product.name} from SmartComputersKE. "
                "Fast delivery, warranty and genuine products."
            )

        if not product.keywords:

            product.keywords = [

                product.name,

                product.brand,

                "Kenya",

                "SmartComputersKE"

            ]

        return product