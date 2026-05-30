from __future__ import annotations

from pathlib import Path

from src.parser.modniy_shopping import fetch_html, parse_product_html, parse_product_page
from src.validation.validator import validate_rows
from src.xlsx.row_builder import build_xlsx_rows
from src.xlsx.writer import write_xlsx_from_template


def generate_import_file(
    product_url: str,
    template_path: str,
    output_dir: str,
    *,
    color_id: str,
    position_title: str,
    position_title_ukr: str,
    price_override: int | None = None,
    debug_html: str | None = None,
) -> str:
    html = fetch_html(product_url)
    if debug_html:
        Path(debug_html).write_text(html, encoding="utf-8")
    return generate_import_file_from_html(
        html,
        product_url,
        template_path,
        output_dir,
        color_id=color_id,
        position_title=position_title,
        position_title_ukr=position_title_ukr,
        price_override=price_override,
    )


def generate_import_file_from_html(
    html: str,
    product_url: str,
    template_path: str,
    output_dir: str,
    *,
    color_id: str,
    position_title: str,
    position_title_ukr: str,
    price_override: int | None = None,
) -> str:
    product = parse_product_html(html, product_url)
    rows = build_xlsx_rows(
        product,
        color_id=color_id,
        position_title=position_title,
        position_title_ukr=position_title_ukr,
        price_override=price_override,
    )
    validate_rows(rows)
    return write_xlsx_from_template(template_path, rows, output_dir)


def parse_only(product_url: str):
    return parse_product_page(product_url)
