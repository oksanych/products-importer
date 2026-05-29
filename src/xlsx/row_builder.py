from __future__ import annotations

import zlib

from src.models.product import Product, SizeVariant
from src.normalizer.sku import format_product_code
from src.normalizer.text import build_description, search_queries, title_for_size


GROUP_NUMBER = "85929329"
GROUP_NAME = "Купальники"
SUBDIVISION_URL = "https://prom.ua/Kupalniki-zhenskie"
SUBDIVISION_ID = "31299"


def numeric_crc32_group_id(product_id: str) -> int:
    return (zlib.crc32(product_id.encode("ascii")) % 900_000_000) + 1


def build_xlsx_rows(product: Product, *, color_id: str, price_override: int | None = None) -> list[dict]:
    rows = []
    group_id = str(numeric_crc32_group_id(product.product_id))
    images = ", ".join(product.images)
    description_uk = build_description(product, "uk")
    description_ru = build_description(product, "ru")
    product_code = format_product_code(product.sku, color_id)
    price = price_override if price_override is not None else product.price

    for size in product.size_table:
        row = {
            "_product_id": product.product_id,
            "_characteristics": build_characteristics(product, size),
            "Код_товару": product_code,
            "Назва_позиції": title_for_size(product, size.ua_size, "ru"),
            "Назва_позиції_укр": title_for_size(product, size.ua_size, "uk"),
            "Пошукові_запити": search_queries(product, "ru"),
            "Пошукові_запити_укр": search_queries(product, "uk"),
            "Опис": description_ru,
            "Опис_укр": description_uk,
            "Тип_товару": "r",
            "Ціна": price,
            "Валюта": product.currency or "UAH",
            "Одиниця_виміру": "шт.",
            "Мінімальний_обсяг_замовлення": "",
            "Оптова_ціна": "",
            "Мінімальне_замовлення_опт": "",
            "Посилання_зображення": images,
            "Наявність": "+",
            "Кількість": "3",
            "Номер_групи": GROUP_NUMBER,
            "Назва_групи": GROUP_NAME,
            "Посилання_підрозділу": SUBDIVISION_URL,
            "Можливість_поставки": "",
            "Термін_поставки": "",
            "Спосіб_пакування": "",
            "Спосіб_пакування_укр": "",
            "Унікальний_ідентифікатор": "",
            "Ідентифікатор_товару": f"modniy-{product.product_id}-{size.ua_size}",
            "Ідентифікатор_підрозділу": SUBDIVISION_ID,
            "Ідентифікатор_групи": "",
            "Виробник": product.brand,
            "Країна_виробник": product.characteristics.get("Країна виробник", ""),
            "Знижка": "",
            "ID_групи_різновидів": group_id,
            "Особисті_нотатки": "",
            "Продукт_на_сайті": product.url,
            "Термін_дії_знижки_від": "",
            "Термін_дії_знижки_до": "",
            "Ціна_від": "-",
            "Ярлик": "",
            "HTML_заголовок": "",
            "HTML_заголовок_укр": "",
            "HTML_опис": "",
            "HTML_опис_укр": "",
            "Подарунки": "",
            "Супутні": "",
            "ID_Подарунків": "",
            "ID_Супутніх": "",
            "Код_маркування_(GTIN)": "",
            "Номер_пристрою_(MPN)": "",
            "Вага,кг": "",
            "Ширина,см": "",
            "Висота,см": "",
            "Довжина,см": "",
            "Де_знаходиться_товар": "",
        }
        rows.append(row)
    return rows


def build_characteristics(product: Product, size: SizeVariant) -> list[tuple[str, str, str]]:
    names = [
        "Тип",
        "Колір",
        "Склад",
        "Тип трусів",
        "Тип тканини",
        "Тип роздільного купальника",
        "Тип злитного купальника",
        "Візерунки і принти",
        "Тип бюстгальтера",
        "Стан",
        "Виробник",
        "Країна виробник",
    ]
    characteristics: list[tuple[str, str, str]] = []
    for name in names:
        value = product.characteristics.get(name)
        if value:
            characteristics.append((name, "", value))
    characteristics.append(("Розмір жіночого одягу (UA)", "", size.ua_size))
    return characteristics[:25]
