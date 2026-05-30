from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from src.main import generate_import_file
from src.normalizer.price import validate_import_price
from src.normalizer.sku import validate_color_id
from src.normalizer.title import (
    PositionTitleValidationError,
    validate_position_title,
    validate_position_title_ukr,
)


ALLOWED_HOST = "modniy-shopping.com.ua"
DEFAULT_TEMPLATE_PATH = Path("templates/export-template.xlsx")
DEFAULT_OUTPUT_ROOT = Path("output/generated-files/ui-runs")
WRONG_DOMAIN_MESSAGE = "Вставте посилання на товар з modniy-shopping.com.ua."
INVALID_COLOR_ID_MESSAGE = "Код кольору має складатися рівно з 2 цифр, наприклад 65."
INVALID_IMPORT_PRICE_MESSAGE = "Ціна має бути цілим числом у гривнях, наприклад 1000."
INVALID_POSITION_TITLE_MESSAGE = "Назва позиції має бути заповнена і не довша за 110 символів з урахуванням розміру."
INVALID_POSITION_TITLE_UKR_MESSAGE = "Назва позиції українською має бути заповнена і не довша за 130 символів з урахуванням розміру."
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
    import_price: str | None,
    position_title: str | None,
    position_title_ukr: str | None,
    *,
    template_path: str | Path = DEFAULT_TEMPLATE_PATH,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    generator: Callable[..., str] | None = None,
) -> GeneratedFile:
    trimmed_url = (product_url or "").strip()
    trimmed_color_id = (color_id or "").strip()
    trimmed_import_price = (import_price or "").strip()
    valid_color_id = _validate_color_id_for_ui(trimmed_color_id)
    valid_import_price = _validate_import_price_for_ui(trimmed_import_price)
    valid_position_title = _validate_position_title_for_ui(position_title)
    valid_position_title_ukr = _validate_position_title_ukr_for_ui(position_title_ukr)
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
                price_override=valid_import_price,
                position_title=valid_position_title,
                position_title_ukr=valid_position_title_ukr,
            )
        )
    except PositionTitleValidationError as error:
        raise InputValidationError(_position_title_message_for_ui(error)) from error
    except Exception as error:
        logger.exception("Failed to generate XLSX for UI request: %s", trimmed_url)
        raise GenerationError(GENERATION_FAILED_MESSAGE) from error

    return GeneratedFile(path=output_path, filename=output_path.name)


def _validate_color_id_for_ui(color_id: str) -> str:
    try:
        return validate_color_id(color_id)
    except ValueError as error:
        raise InputValidationError(INVALID_COLOR_ID_MESSAGE) from error


def _validate_import_price_for_ui(import_price: str) -> int:
    try:
        return validate_import_price(import_price)
    except ValueError as error:
        raise InputValidationError(INVALID_IMPORT_PRICE_MESSAGE) from error


def _validate_position_title_for_ui(position_title: str | None) -> str:
    try:
        return validate_position_title(position_title)
    except PositionTitleValidationError as error:
        raise InputValidationError(INVALID_POSITION_TITLE_MESSAGE) from error


def _validate_position_title_ukr_for_ui(position_title_ukr: str | None) -> str:
    try:
        return validate_position_title_ukr(position_title_ukr)
    except PositionTitleValidationError as error:
        raise InputValidationError(INVALID_POSITION_TITLE_UKR_MESSAGE) from error


def _position_title_message_for_ui(error: PositionTitleValidationError) -> str:
    if error.field == "position_title_ukr":
        return INVALID_POSITION_TITLE_UKR_MESSAGE
    return INVALID_POSITION_TITLE_MESSAGE


def _validate_product_url(product_url: str) -> None:
    parsed = urlparse(product_url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise InputValidationError(WRONG_DOMAIN_MESSAGE)
