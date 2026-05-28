from __future__ import annotations

import re


REQUIRED_COLUMNS = [
    "Назва_позиції",
    "Назва_позиції_укр",
    "Ціна",
    "Валюта",
    "Посилання_зображення",
    "Ідентифікатор_товару",
    "ID_групи_різновидів",
]


def validate_rows(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("No rows generated")

    item_ids: set[str] = set()
    char_names_by_group: dict[str, tuple[str, ...]] = {}

    for index, row in enumerate(rows, start=1):
        _validate_required_fields(row, index)
        _validate_empty_columns(row, index)
        _validate_variant_group_id(row, index)
        _validate_forbidden_terms(row, index)
        _validate_characteristics(row, index, char_names_by_group)

        item_id = row.get("Ідентифікатор_товару", "")
        if item_id in item_ids:
            raise ValueError(f"Row {index}: duplicate Ідентифікатор_товару {item_id}")
        item_ids.add(item_id)


def _validate_required_fields(row: dict, row_index: int) -> None:
    for column in REQUIRED_COLUMNS:
        if not str(row.get(column) or "").strip():
            raise ValueError(f"Row {row_index}: required field {column} is empty")


def _validate_empty_columns(row: dict, row_index: int) -> None:
    for column in ["Оптова_ціна", "Мінімальне_замовлення_опт", "Подарунки", "ID_Подарунків", "Супутні", "ID_Супутніх"]:
        if row.get(column):
            raise ValueError(f"Row {row_index}: {column} should be empty")


def _validate_variant_group_id(row: dict, row_index: int) -> None:
    value = str(row.get("ID_групи_різновидів") or "")
    if not value.isdigit():
        raise ValueError(f"Row {row_index}: ID_групи_різновидів should be numeric")
    number = int(value)
    if number < 0 or number > 999_999_999:
        raise ValueError(f"Row {row_index}: ID_групи_різновидів is outside Prom range")


def _validate_forbidden_terms(row: dict, row_index: int) -> None:
    columns = ["Назва_позиції", "Назва_позиції_укр", "Пошукові_запити", "Пошукові_запити_укр", "Опис", "Опис_укр"]
    pattern = re.compile(r"\b[A-ZА-ЯІЇЄҐ][A-Za-zА-Яа-яІіЇїЄєҐґ]+\s+\d{4,}(?:-\d+)?\b")
    for column in columns:
        value = str(row.get(column) or "")
        if pattern.search(value):
            raise ValueError(f"Row {row_index}: service code found in {column}")


def _validate_characteristics(row: dict, row_index: int, char_names_by_group: dict[str, tuple[str, ...]]) -> None:
    characteristics = row.get("_characteristics") or []
    if len(characteristics) > 25:
        raise ValueError(f"Row {row_index}: too many characteristics")
    names = tuple(name for name, _unit, _value in characteristics)
    if "Розмір жіночого одягу (UA)" not in names:
        raise ValueError(f"Row {row_index}: missing variant size characteristic")
    group_id = str(row.get("ID_групи_різновидів") or "")
    if group_id in char_names_by_group and char_names_by_group[group_id] != names:
        raise ValueError(f"Row {row_index}: inconsistent characteristics for variant group")
    char_names_by_group.setdefault(group_id, names)

