from __future__ import annotations

import argparse
from pathlib import Path

from src.main import generate_import_file, generate_import_file_from_html
from src.normalizer.price import validate_import_price
from src.normalizer.sku import validate_color_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Prom XLSX import from a modniy-shopping product URL.")
    parser.add_argument("url", help="Product URL from modniy-shopping.com.ua")
    parser.add_argument("--template", default="templates/export-template.xlsx", help="Prom export/template XLSX path")
    parser.add_argument("--output-dir", default="output/generated-files", help="Directory for generated XLSX files")
    parser.add_argument("--debug-html", help="Optional path where fetched HTML should be saved")
    parser.add_argument("--from-html", help="Read source HTML from a local file instead of fetching the URL")
    parser.add_argument("--color-id", nargs="?", help="Required 2-digit color identifier, for example 65")
    parser.add_argument("--import-price", nargs="?", help="Required import price in whole UAH, for example 1000")
    args = parser.parse_args()

    try:
        color_id = validate_color_id(args.color_id)
    except ValueError as error:
        parser.error(str(error))

    try:
        import_price = validate_import_price(args.import_price)
    except ValueError as error:
        parser.error(str(error))

    if args.from_html:
        html = Path(args.from_html).read_text(encoding="utf-8")
        output = generate_import_file_from_html(
            html,
            args.url,
            args.template,
            args.output_dir,
            color_id=color_id,
            price_override=import_price,
        )
    else:
        output = generate_import_file(
            args.url,
            args.template,
            args.output_dir,
            color_id=color_id,
            price_override=import_price,
            debug_html=args.debug_html,
        )
    print(f"Generated file: {output}")


if __name__ == "__main__":
    main()
