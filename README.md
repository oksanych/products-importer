# Product Importer MVP

Local CLI that turns a `modniy-shopping.com.ua` product page into a Prom-compatible XLSX import file.

## Requirements

- Python 3.9+
- Internet access for live product parsing

## Setup

Clone the repository and enter the project root:

```bash
git clone <repo-url>
cd product-importer-mvp
```

Create a local virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

For later runs from a new terminal window, activate the same virtual environment first:

```bash
source .venv/bin/activate
```

## Generate XLSX

Generate an XLSX from a live product page:

```bash
python3 generate_import.py "https://modniy-shopping.com.ua/ua/p3064637917-slitnyj-kupalnik-fuba.html" --color-id 65
```

`--color-id` is required and must be exactly two digits. It is added to `Код_товару`.

By default, generated files are saved to:

```text
output/generated-files/
```

The generated file name uses the source product ID:

```text
output/generated-files/import-products-3064637917.xlsx
```

To choose another output directory, pass `--output-dir`:

```bash
python3 generate_import.py "https://modniy-shopping.com.ua/ua/p3064637917-slitnyj-kupalnik-fuba.html" --color-id 65 --output-dir output/live-test
```

## Local Browser UI

Start the local UI:

```bash
python3 run_ui.py
```

The app opens at:

```text
http://127.0.0.1:8000
```

It accepts a `modniy-shopping.com.ua` product URL and a required 2-digit color ID, then downloads the generated Prom XLSX file. UI-generated files are saved in unique run folders under:

```text
output/generated-files/ui-runs/
```

To start the UI without opening a browser automatically:

```bash
python3 run_ui.py --no-browser
```

## Fixture Testing

Generate from a local fixture without fetching the live page:

```bash
python3 generate_import.py "https://modniy-shopping.com.ua/ua/p3064637917-slitnyj-kupalnik-fuba.html" --from-html fixtures/modniy_3064637917.html --color-id 65
```

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'lxml'`, activate the virtual environment and reinstall dependencies:

```bash
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```
