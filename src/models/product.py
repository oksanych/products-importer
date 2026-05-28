from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SizeVariant:
    ua_size: str
    intl_size: str | None = None
    label_size: str | None = None
    hips: str | None = None
    cup: str | None = None


@dataclass
class Product:
    url: str
    product_id: str
    name: str
    sku: str
    brand: str
    price: str
    currency: str = "UAH"
    availability: str = ""
    description: str = ""
    images: list[str] = field(default_factory=list)
    characteristics: dict[str, str] = field(default_factory=dict)
    size_table: list[SizeVariant] = field(default_factory=list)
