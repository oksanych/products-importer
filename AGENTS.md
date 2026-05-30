# AGENTS.md

## Project

This is a local Python CLI that generates Prom-compatible XLSX import files from `modniy-shopping.com.ua` product pages.

## Setup

Use Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Commands

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Generate from a live URL:

```bash
python3 generate_import.py "<product-url>" --color-id 65 --import-price 1000 --position-title "Купальник жіночий чорний" --position-title-ukr "Купальник жіночий чорний"
```

Generate from fixture:

```bash
python3 generate_import.py "<product-url>" --from-html fixtures/modniy_3064637917.html --color-id 65 --import-price 1000 --position-title "Купальник жіночий чорний" --position-title-ukr "Купальник жіночий чорний"
```

## Important Rules

- Do not commit `.venv/`, `output/`, `__pycache__/`, `.DS_Store`, or generated XLSX files.
- Keep `templates/export-template.xlsx` sanitized:
  - `Export Products Sheet` must contain only the header row.
  - `Export Groups Sheet` must keep only the existing Modashop root category `31935910 / Купальники`.
- Keep `--color-id` required and exactly two digits.
- Keep `--import-price` required and a whole UAH amount.
- Keep `--position-title` and `--position-title-ukr` required.
- Keep final generated `Назва_позиції` at most 110 characters and `Назва_позиції_укр` at most 130 characters after appending size.
- `Код_товару` format is `MS` + SKU without trailing `-digits` + color ID.
- Do not change `Ідентифікатор_товару` format without checking Prom documentation.
- For new products, keep `Унікальний_ідентифікатор` empty.
- Variant grouping must use one changing characteristic: `Розмір жіночого одягу (UA)`.

## Verification

Before finishing changes, run:

```bash
python3 -m unittest discover -s tests -v
```

For XLSX-related changes, also generate one fixture XLSX and inspect that:

- product sheet has 128 columns;
- group sheet has only `31935910 / Купальники`;
- generated rows have empty `Унікальний_ідентифікатор`;
- `ID_групи_різновидів` is numeric and shared across sizes.
