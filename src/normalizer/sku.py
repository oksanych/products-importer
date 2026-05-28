from __future__ import annotations

import re


COLOR_PARAMETER_ERROR = "Check color parameter: --color-id is required and must be exactly 2 digits, for example --color-id 65"


def validate_color_id(value: str | None) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}", value):
        raise ValueError(COLOR_PARAMETER_ERROR)
    return value


def format_product_code(sku: str, color_id: str) -> str:
    validated_color_id = validate_color_id(color_id)
    base_sku = re.sub(r"-\d+$", "", str(sku or "").strip())
    return f"MS{base_sku}{validated_color_id}"
