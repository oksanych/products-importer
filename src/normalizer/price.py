from __future__ import annotations


PRICE_PARAMETER_ERROR = (
    "Check price parameter: --import-price is required and must be a whole UAH amount, "
    "for example --import-price 1000"
)
MAX_IMPORT_PRICE = 9_999_999_999


def validate_import_price(value: str | None) -> int:
    if not isinstance(value, str):
        raise ValueError(PRICE_PARAMETER_ERROR)

    normalized = value.strip().replace(",", ".")
    if normalized.endswith(".00"):
        normalized = normalized[:-3]
    if not normalized.isdigit():
        raise ValueError(PRICE_PARAMETER_ERROR)

    price = int(normalized)
    if price < 1 or price > MAX_IMPORT_PRICE:
        raise ValueError(PRICE_PARAMETER_ERROR)
    return price
