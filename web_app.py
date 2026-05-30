from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app_service import AppServiceError, generate_from_user_input


BASE_DIR = Path(__file__).resolve().parent
XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

app = FastAPI(title="Product Importer UI")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return _render_form(request)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/generate")
def generate(
    request: Request,
    product_url: str = Form(...),
    color_id: str = Form(...),
    import_price: str = Form(...),
    position_title: str = Form(...),
    position_title_ukr: str = Form(...),
):
    try:
        generated = generate_from_user_input(
            product_url,
            color_id,
            import_price,
            position_title,
            position_title_ukr,
        )
    except AppServiceError as error:
        if request.headers.get("x-requested-with") == "fetch":
            return JSONResponse(
                {"error": error.user_message},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return _render_form(
            request,
            error=error.user_message,
            product_url=product_url,
            color_id=color_id,
            import_price=import_price,
            position_title=position_title,
            position_title_ukr=position_title_ukr,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return FileResponse(
        path=generated.path,
        filename=generated.filename,
        media_type=XLSX_MEDIA_TYPE,
    )


def _render_form(
    request: Request,
    *,
    error: str | None = None,
    product_url: str = "",
    color_id: str = "",
    import_price: str = "",
    position_title: str = "",
    position_title_ukr: str = "",
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "error": error,
            "product_url": product_url,
            "color_id": color_id,
            "import_price": import_price,
            "position_title": position_title,
            "position_title_ukr": position_title_ukr,
        },
        status_code=status_code,
    )
