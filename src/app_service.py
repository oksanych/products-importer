from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from src.main import generate_import_file
from src.normalizer.sku import validate_color_id


ALLOWED_HOST = "modniy-shopping.com.ua"
DEFAULT_TEMPLATE_PATH = Path("templates/export-template.xlsx")
DEFAULT_OUTPUT_ROOT = Path("output/generated-files/ui-runs")
WRONG_DOMAIN_MESSAGE = "Вставте посилання на товар з modniy-shopping.com.ua."
INVALID_COLOR_ID_MESSAGE = "Код кольору має складатися рівно з 2 цифр, наприклад 65."
GENERATION_FAILED_MESSAGE = "Не вдалося згенерувати файл. Перевірте посилання або спробуйте інший товар."

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedFile:
    path: Path
    filename: str


class AppServiceError(Exception):
    def __init__(self, user_message: str) -> None:
        super().__init__(user_message)
        self.user_message = user_message


class InputValidationError(AppServiceError):
    pass


class GenerationError(AppServiceError):
    pass


def generate_from_user_input(
    product_url: str | None,
    color_id: str | None,
    *,
    template_path: str | Path = DEFAULT_TEMPLATE_PATH,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    generator: Callable[..., str] | None = None,
) -> GeneratedFile:
    trimmed_url = (product_url or "").strip()
    trimmed_color_id = (color_id or "").strip()
    valid_color_id = _validate_color_id_for_ui(trimmed_color_id)
    _validate_product_url(trimmed_url)

    run_dir = Path(output_root) / uuid.uuid4().hex
    generator_func = generator or generate_import_file

    try:
        output_path = Path(
            generator_func(
                trimmed_url,
                str(template_path),
                str(run_dir),
                color_id=valid_color_id,
            )
        )
    except Exception as error:
        logger.exception("Failed to generate XLSX for UI request: %s", trimmed_url)
        raise GenerationError(GENERATION_FAILED_MESSAGE) from error

    return GeneratedFile(path=output_path, filename=output_path.name)


def _validate_color_id_for_ui(color_id: str) -> str:
    try:
        return validate_color_id(color_id)
    except ValueError as error:
        raise InputValidationError(INVALID_COLOR_ID_MESSAGE) from error


def _validate_product_url(product_url: str) -> None:
    parsed = urlparse(product_url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise InputValidationError(WRONG_DOMAIN_MESSAGE)
