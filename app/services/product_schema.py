from dataclasses import dataclass, field


@dataclass
class ImportedProduct:

    name: str = ""

    brand: str = ""

    category: str = ""

    description: str = ""

    short_description: str = ""

    sku: str = ""

    model: str = ""

    price: float | None = None

    currency: str = "KES"

    seo_title: str = ""

    meta_description: str = ""

    keywords: list[str] = field(default_factory=list)

    images: list[str] = field(default_factory=list)

    specifications: dict = field(default_factory=dict)