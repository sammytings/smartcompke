from django.utils.text import slugify

from app.models import Category


class CategoryService:
    """
    Creates category hierarchy from WooCommerce.

    Example:

    Computers > Laptops > Gaming
    """

    SEPARATORS = [
        ">",
        "|",
    ]

    @classmethod
    def get_category(cls, row):

        raw = row.get("Categories", "").strip()

        if not raw:
            return None

        raw = raw.replace("&gt;", ">")

        parts = cls.split_categories(raw)

        parent = None
        current = None

        for name in parts:

            slug = slugify(name)

            defaults = {
                "slug": slug,
            }

            try:

                category = Category.objects.get(name=name)

                if (
                    hasattr(category, "parent")
                    and category.parent != parent
                ):
                    category.parent = parent
                    category.save(update_fields=["parent"])

            except Category.DoesNotExist:

                kwargs = {
                    "name": name,
                    "defaults": defaults,
                }

                if "parent" in [
                    f.name for f in Category._meta.fields
                ]:
                    kwargs["parent"] = parent

                category, _ = Category.objects.get_or_create(
                    **kwargs
                )

            parent = category
            current = category

        return current

    @classmethod
    def split_categories(cls, text):

        for sep in cls.SEPARATORS:

            if sep in text:

                return [
                    x.strip()
                    for x in text.split(sep)
                    if x.strip()
                ]

        # WooCommerce exports multiple categories separated by commas.
        # Use the first category only.

        return [
            text.split(",")[0].strip()
        ]