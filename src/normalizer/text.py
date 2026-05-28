from __future__ import annotations

import re

from src.models.product import Product


UK_RU_REPLACEMENTS = {
    "Злитий": "Слитный",
    "злитий": "слитный",
    "Жіночий": "Женский",
    "жіночий": "женский",
    "купальник": "купальник",
    "Танкіні": "Танкини",
    "танкіні": "танкини",
    "плавками": "плавками",
    "коричневий": "коричневый",
    "чорний": "черный",
    "чорний-білий": "черно-белый",
    "синій": "синий",
    "шнурівкою": "шнуровкой",
    "кісточках": "косточках",
    "розмір": "размер",
    "зі": "со",
    "на": "на",
    "сатин": "сатин",
}


def base_title(product: Product) -> str:
    title = remove_service_model_code(product.name, product.brand, product.sku)
    title = re.sub(r"(?:\s+\d{2}){2,}\s+розмір\b", "", title, flags=re.I)
    return _collapse(title)


def title_for_size(product: Product, size: str, language: str) -> str:
    title = base_title(product)
    if language == "ru":
        title = translate_uk_to_ru(title)
    return _collapse(f"{title} {size}")


def build_description(product: Product, language: str) -> str:
    title = title_for_size(product, product.size_table[0].ua_size if product.size_table else "", language).strip()
    description = product.description
    if language == "ru":
        title = translate_uk_to_ru(title)
        description = translate_uk_to_ru(description)
    description = remove_service_model_code(description, product.brand, product.sku)
    table = _size_table_html(product)
    return "\n".join(
        part
        for part in [
            f"<h2>{title}</h2>",
            f"<p>{description}</p>" if description else "",
            table,
        ]
        if part
    )


def search_queries(product: Product, language: str) -> str:
    sizes = [item.ua_size for item in product.size_table]
    color = product.characteristics.get("Колір", "")
    if language == "ru":
        color = translate_uk_to_ru(color).lower()
        queries = [
            "купальник женский",
            "женский купальник",
            "купальник больших размеров",
            "купальник для бассейна",
        ]
        if "Танкіні" in product.name:
            queries.append("танкини женский")
    else:
        queries = [
            "купальник жіночий",
            "жіночий купальник",
            "купальник великих розмірів",
            "купальник для басейну",
        ]
        if "Танкіні" in product.name:
            queries.append("танкіні жіночий")
    if color:
        queries.append(f"купальник {color}")
    for size in sizes:
        queries.append(f"купальник {size}")
    return ", ".join(dict.fromkeys(queries))


def remove_service_model_code(text: str, brand: str, sku: str) -> str:
    result = text or ""
    if brand and sku:
        result = re.sub(rf"\b{re.escape(brand)}\s+{re.escape(sku)}\b", "", result, flags=re.I)
    return _collapse(result)


def translate_uk_to_ru(text: str) -> str:
    result = text or ""
    for uk, ru in sorted(UK_RU_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"\b{re.escape(uk)}\b", ru, result)
    return _collapse(result)


def _size_table_html(product: Product) -> str:
    if not product.size_table:
        return ""
    rows = [
        "<table>",
        "<tr><th>Український розмір</th><th>Міжнародний розмір</th><th>На бірці</th><th>Обхват стегон</th><th>Чашка</th></tr>",
    ]
    for item in product.size_table:
        rows.append(
            "<tr>"
            f"<td>{item.ua_size}</td>"
            f"<td>{item.intl_size or ''}</td>"
            f"<td>{item.label_size or ''}</td>"
            f"<td>{item.hips or ''}</td>"
            f"<td>{item.cup or ''}</td>"
            "</tr>"
        )
    rows.append("</table>")
    return "".join(rows)


def _collapse(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    return value

