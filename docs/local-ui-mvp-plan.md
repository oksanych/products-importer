# Local Products Importer UI MVP Plan

## Goal

Add a simple local browser UI for generating Prom-compatible XLSX files from `modniy-shopping.com.ua` product pages.

This plan covers local usage only. It does not include VPS deployment, DNS, Nginx, SSL, systemd, authentication, or public hosting.

## Recommended Approach

Use a small FastAPI app with Jinja2 templates and plain CSS.

The UI should wrap the existing generation logic instead of replacing the CLI. The current CLI must keep working exactly as before.

Local flow:

```text
User opens http://127.0.0.1:8000
-> enters product URL and 2-digit color ID
-> FastAPI validates input
-> existing core generates XLSX
-> browser downloads the file
```

## Scope

Included:

- Local web form with product URL and color ID fields.
- XLSX download after successful generation.
- Friendly validation and error messages.
- A small service layer between the UI and the existing core.
- Tests for service logic and UI routes.
- README instructions for local UI usage.

Not included:

- VPS deployment.
- Authentication.
- Nginx, Certbot, systemd, DNS, firewall setup.
- Batch import.
- Generation history.
- Editing parsed product data before export.

## Proposed Files

Create:

- `src/app_service.py`
- `web_app.py`
- `templates/index.html`
- `static/style.css`
- `run_ui.py`
- `tests/test_app_service.py`
- `tests/test_web_app.py`

Modify:

- `requirements.txt`
- `pyproject.toml`
- `README.md`

## Dependencies

Add:

```txt
fastapi>=0.115,<1
uvicorn[standard]>=0.30,<1
jinja2>=3.1,<4
python-multipart>=0.0.9,<1
httpx>=0.27,<1
```

`httpx` is needed for FastAPI `TestClient` tests.

## Service Layer

Add `src/app_service.py`.

Responsibilities:

- Trim user input.
- Validate `color_id` with the existing `validate_color_id`.
- Validate URL using `urllib.parse.urlparse`.
- Allow only:
  - scheme: `https`
  - host: `modniy-shopping.com.ua`
- Call `generate_import_file`.
- Use a unique per-request output directory under:

```text
output/generated-files/ui-runs/
```

This prevents repeated UI generation for the same product from overwriting previous files.

## FastAPI UI

Add `web_app.py`.

Routes:

- `GET /`
  - renders the form;
  - no auth;
  - intended for local-only usage.
- `POST /generate`
  - accepts `product_url` and `color_id`;
  - calls `generate_from_user_input`;
  - returns XLSX via `FileResponse`;
  - on validation or generation error, re-renders the form with a friendly message.

The app should bind only to:

```text
127.0.0.1
```

## Local Runner

Add `run_ui.py`.

Expected command:

```bash
python3 run_ui.py
```

Expected behavior:

- starts Uvicorn on `127.0.0.1:8000`;
- optionally opens `http://127.0.0.1:8000` in the default browser;
- does not expose the app on the local network.

## UX Requirements

The page should be simple and friendly:

- clear title;
- product URL input;
- color ID input with example `65`;
- submit button;
- optional loading or disabled state while generation is running;
- clear error message for invalid input or failed generation.

Do not show raw stack traces in the browser.

## Error Handling

Friendly messages:

- Wrong domain:

```text
Вставте посилання на товар з modniy-shopping.com.ua.
```

- Invalid color ID:

```text
Код кольору має складатися рівно з 2 цифр, наприклад 65.
```

- Generation failure:

```text
Не вдалося згенерувати файл. Перевірте посилання або спробуйте інший товар.
```

Technical details should go to logs, not the UI.

## Test Plan

Run existing tests:

```bash
python3 -m unittest discover -s tests -v
```

Add service tests:

- rejects wrong domain;
- rejects non-HTTPS URL;
- rejects invalid color ID;
- trims input;
- returns generated file metadata for valid input with mocked generator.

Add FastAPI route tests:

- `GET /` returns `200`;
- form page contains product URL and color ID fields;
- invalid `POST /generate` returns `400`;
- valid `POST /generate` returns XLSX media type with mocked service.

Manual check:

1. Run:

```bash
python3 run_ui.py
```

2. Open:

```text
http://127.0.0.1:8000
```

3. Generate XLSX for 2-3 real product URLs.
4. Open the XLSX in Excel, LibreOffice, or Google Sheets.
5. Confirm CLI still works:

```bash
python3 generate_import.py "https://modniy-shopping.com.ua/ua/p3064637917-slitnyj-kupalnik-fuba.html" --color-id 65
```

## Definition of Done

The local UI MVP is done when:

- all existing CLI tests pass;
- new service/UI tests pass;
- `python3 run_ui.py` starts the local UI;
- the form generates and downloads XLSX;
- invalid input shows friendly messages;
- repeated generation of the same product does not overwrite earlier UI output;
- README explains how to run the local UI;
- no deployment, security, or VPS changes are included.
