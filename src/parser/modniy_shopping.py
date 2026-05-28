from __future__ import annotations

import json
import re
import urllib.request
from html import unescape

from lxml import html as lxml_html

from src.models.product import Product, SizeVariant


def fetch_html(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def parse_product_page(url: str) -> Product:
    return parse_product_html(fetch_html(url), url)


def parse_product_html(html: str, url: str) -> Product:
    doc = lxml_html.fromstring(html)
    product_json = _extract_product_json(doc)
    if not product_json:
        raise ValueError("Cannot find JSON-LD Product data")

    name = _clean(product_json.get("name"))
    product_id = extract_product_id(url) or _extract_product_id_from_html(doc)
    sku = _clean(product_json.get("sku")) or product_id
    brand = _extract_brand(product_json.get("brand"))
    offers = product_json.get("offers") if isinstance(product_json.get("offers"), dict) else {}

    characteristics = _extract_characteristics(doc)
    images = _extract_images(doc, product_json)
    description = _clean(product_json.get("description"))
    size_table = _extract_size_table(doc)
    if not size_table:
        size_table = _sizes_from_title(name)

    return Product(
        url=url,
        product_id=product_id,
        name=name,
        sku=sku,
        brand=brand,
        price=_clean(offers.get("price")),
        currency=_clean(offers.get("priceCurrency")) or "UAH",
        availability=_clean(offers.get("availability")),
        description=description,
        images=images,
        characteristics=characteristics,
        size_table=size_table,
    )


def extract_product_id(url: str) -> str:
    match = re.search(r"/p(\d+)-", url)
    if match:
        return match.group(1)
    match = re.search(r"\bp(\d+)\b", url)
    return match.group(1) if match else ""


def _extract_product_json(doc) -> dict:
    for script in doc.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
    return {}


def _extract_product_id_from_html(doc) -> str:
    for value in doc.xpath('//*[@data-product-id]/@data-product-id | //*[@data-advtracking-product-id]/@data-advtracking-product-id'):
        value = _clean(value)
        if value.isdigit():
            return value
    raise ValueError("Cannot extract product ID")


def _extract_brand(raw_brand) -> str:
    if isinstance(raw_brand, dict):
        return _clean(raw_brand.get("name"))
    return _clean(raw_brand)


def _extract_characteristics(doc) -> dict[str, str]:
    result: dict[str, str] = {}
    rows = doc.xpath('//table[@data-qaid="characteristics_block"]//tr[@data-qaid="attribute_item"]')
    for row in rows:
        name = _clean(" ".join(row.xpath('.//*[@data-qaid="attribute_name"]//text()')))
        value = _clean(" ".join(row.xpath('.//*[@data-qaid="attribute_value"]//text()')))
        if name and value:
            result[name] = value
    return result


def _extract_images(doc, product_json: dict) -> list[str]:
    candidates: list[str] = []
    candidates.extend(doc.xpath('//meta[@property="og:image"]/@content'))
    image = product_json.get("image")
    if isinstance(image, str):
        candidates.append(image)
    elif isinstance(image, list):
        candidates.extend(str(item) for item in image)
    candidates.extend(doc.xpath('//*[@data-cspgo-image-id]/@src'))
    candidates.extend(doc.xpath('//a[contains(@class, "js-product-gallery-overlay")]/@href'))

    seen_ids: set[str] = set()
    images: list[str] = []
    for candidate in candidates:
        normalized = _normalize_image_url(candidate)
        if not normalized:
            continue
        image_id = normalized.split("/")[3].split("_", 1)[0]
        if image_id in seen_ids:
            continue
        seen_ids.add(image_id)
        images.append(normalized)
    return images


def _normalize_image_url(value: str) -> str:
    value = unescape(value or "")
    match = re.search(r"https://images\.prom\.ua/(\d+)(?:_[^/\s<>]+)?_([^/\s<>]+?\.(?:jpg|jpeg|png|webp))", value, re.I)
    if not match:
        return ""
    return f"https://images.prom.ua/{match.group(1)}_w640_h640_{match.group(2)}"


def _extract_size_table(doc) -> list[SizeVariant]:
    for table in doc.xpath('//table[not(@data-qaid="characteristics_block")]'):
        rows = _table_rows(table)
        parsed = _parse_size_rows(rows)
        if parsed:
            return parsed
    return []


def _table_rows(table) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.xpath(".//tr"):
        cells = [_clean(" ".join(cell.xpath(".//text()"))) for cell in tr.xpath("./th|./td")]
        cells = [cell for cell in cells if cell]
        if cells:
            rows.append(cells)
    return rows


def _parse_size_rows(rows: list[list[str]]) -> list[SizeVariant]:
    if not rows:
        return []
    if _looks_like_vertical_table(rows):
        parsed = _parse_vertical_size_rows(rows)
        if parsed:
            return parsed
    if _looks_like_horizontal_table(rows):
        parsed = _parse_horizontal_size_rows(rows)
        if parsed:
            return parsed
    return []


def _looks_like_horizontal_table(rows: list[list[str]]) -> bool:
    return any(_is_ua_size_label(row[0]) and len(row) > 1 for row in rows)


def _looks_like_vertical_table(rows: list[list[str]]) -> bool:
    return bool(rows and any(_is_ua_size_label(cell) for cell in rows[0]))


def _parse_horizontal_size_rows(rows: list[list[str]]) -> list[SizeVariant]:
    size_row = _find_row(rows, _is_ua_size_label)
    if not size_row:
        return []
    label_row = _find_row(rows, _is_label_size_label)
    hips_row = _find_row(rows, _is_hips_label)
    cup_row = _find_row(rows, _is_cup_label)

    variants: list[SizeVariant] = []
    for index, raw_size in enumerate(size_row[1:], start=1):
        ua_size, intl_size = _parse_combined_size(raw_size)
        if not ua_size:
            continue
        variants.append(
            SizeVariant(
                ua_size=ua_size,
                intl_size=intl_size,
                label_size=_optional_cell(label_row, index),
                hips=_optional_cell(hips_row, index),
                cup=_optional_cell(cup_row, index),
            )
        )
    return variants


def _parse_vertical_size_rows(rows: list[list[str]]) -> list[SizeVariant]:
    header = rows[0]
    ua_index = _find_col(header, _is_ua_size_label)
    label_index = _find_col(header, _is_label_size_label)
    hips_index = _find_col(header, _is_hips_label)
    cup_index = _find_col(header, _is_cup_label)
    if ua_index is None:
        return []

    variants: list[SizeVariant] = []
    for row in rows[1:]:
        if ua_index >= len(row):
            continue
        ua_size, intl_size = _parse_combined_size(row[ua_index])
        if not ua_size:
            continue
        variants.append(
            SizeVariant(
                ua_size=ua_size,
                intl_size=intl_size,
                label_size=_optional_cell(row, label_index),
                hips=_optional_cell(row, hips_index),
                cup=_optional_cell(row, cup_index),
            )
        )
    return variants


def _sizes_from_title(title: str) -> list[SizeVariant]:
    before_marker = re.split(r"\bрозмір\b", title, maxsplit=1, flags=re.I)[0]
    matches = re.findall(r"(?<![-\d])(?:4[0-9]|5[0-9]|6[0-9]|70)(?![-\d])", before_marker)
    unique = list(dict.fromkeys(matches))
    return [SizeVariant(ua_size=size) for size in unique]


def _parse_combined_size(value: str) -> tuple[str, str | None]:
    value = _clean(value)
    match = re.match(r"^(\d{2})\s*[-–]\s*([A-Za-zА-Яа-я0-9]+)$", value)
    if match:
        return match.group(1), _normalize_latin_x(match.group(2).upper())
    if re.match(r"^\d{2}$", value):
        return value, None
    return "", None


def _normalize_latin_x(value: str) -> str:
    return value.replace("Х", "X")


def _find_row(rows: list[list[str]], predicate) -> list[str] | None:
    for row in rows:
        if row and predicate(row[0]):
            return row
    return None


def _find_col(row: list[str], predicate) -> int | None:
    for index, cell in enumerate(row):
        if predicate(cell):
            return index
    return None


def _optional_cell(row: list[str] | None, index: int | None) -> str | None:
    if row is None or index is None or index >= len(row):
        return None
    return _clean(row[index]) or None


def _is_ua_size_label(value: str) -> bool:
    value = value.lower()
    return "український розмір" in value or "украинский размер" in value


def _is_label_size_label(value: str) -> bool:
    value = value.lower()
    return "бірц" in value or "бирц" in value or "етикет" in value or "маркування" in value


def _is_hips_label(value: str) -> bool:
    value = value.lower()
    return "стегон" in value or "бедер" in value


def _is_cup_label(value: str) -> bool:
    value = value.lower()
    return "чаш" in value or "груд" in value


def _clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()
