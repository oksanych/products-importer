from __future__ import annotations

import re


POSITION_TITLE_MAX_LENGTH = 110
POSITION_TITLE_UKR_MAX_LENGTH = 130
POSITION_TITLE_PARAMETER_ERROR = (
    "Check position title parameter: --position-title is required and Назва_позиції "
    "must be 110 characters or less after appending size"
)
POSITION_TITLE_UKR_PARAMETER_ERROR = (
    "Check Ukrainian position title parameter: --position-title-ukr is required and Назва_позиції_укр "
    "must be 130 characters or less after appending size"
)


class PositionTitleValidationError(ValueError):
    def __init__(self, message: str, field: str) -> None:
        super().__init__(message)
        self.field = field


def validate_position_title(value: str | None) -> str:
    return _validate_title(
        value,
        field="position_title",
        max_length=POSITION_TITLE_MAX_LENGTH,
        error_message=POSITION_TITLE_PARAMETER_ERROR,
    )


def validate_position_title_ukr(value: str | None) -> str:
    return _validate_title(
        value,
        field="position_title_ukr",
        max_length=POSITION_TITLE_UKR_MAX_LENGTH,
        error_message=POSITION_TITLE_UKR_PARAMETER_ERROR,
    )


def position_title_for_size(title: str, size: str) -> str:
    return _title_for_size(
        title,
        size,
        field="position_title",
        max_length=POSITION_TITLE_MAX_LENGTH,
        error_message=POSITION_TITLE_PARAMETER_ERROR,
    )


def position_title_ukr_for_size(title: str, size: str) -> str:
    return _title_for_size(
        title,
        size,
        field="position_title_ukr",
        max_length=POSITION_TITLE_UKR_MAX_LENGTH,
        error_message=POSITION_TITLE_UKR_PARAMETER_ERROR,
    )


def _title_for_size(title: str, size: str, *, field: str, max_length: int, error_message: str) -> str:
    normalized_title = _validate_title(title, field=field, max_length=max_length, error_message=error_message)
    titled_size = _collapse(f"{normalized_title} {size}")
    if len(titled_size) > max_length:
        raise PositionTitleValidationError(error_message, field)
    return titled_size


def _validate_title(value: str | None, *, field: str, max_length: int, error_message: str) -> str:
    if not isinstance(value, str):
        raise PositionTitleValidationError(error_message, field)

    normalized = _collapse(value)
    if not normalized or len(normalized) > max_length:
        raise PositionTitleValidationError(error_message, field)
    return normalized


def _collapse(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
