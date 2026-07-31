from .models import ProductAnalytics, Product

from app.services.analytics import AnalyticsService
class ProductViewMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        try:

            if request.resolver_match:

                if request.resolver_match.url_name == "product_detail":

                    slug = request.resolver_match.kwargs.get("slug")

                    if slug:

                        product = Product.objects.filter(
                            slug=slug
                        ).first()

                        if product:

                            analytics, created = ProductAnalytics.objects.get_or_create(
                                product=product
                            )

                            AnalyticsService.record_view(product)

        except Exception:
            pass

        return response