import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.validation.validator import validate_rows


class ValidationTests(unittest.TestCase):
    def base_row(self):
        return {
            "Назва_позиції": "Купальник жіночий 48",
            "Назва_позиції_укр": "Купальник жіночий 48",
            "Ціна": "763.00",
            "Валюта": "UAH",
            "Посилання_зображення": "https://images.prom.ua/example.jpg",
            "Унікальний_ідентифікатор": "",
            "Ідентифікатор_товару": "modniy-1-48",
            "ID_групи_різновидів": "123",
            "Оптова_ціна": "",
            "Мінімальне_замовлення_опт": "",
            "Подарунки": "",
            "ID_Подарунків": "",
            "Супутні": "",
            "ID_Супутніх": "",
            "_characteristics": [("Розмір жіночого одягу (UA)", "", "48")],
        }

    def test_accepts_valid_rows(self):
        validate_rows([self.base_row()])

    def test_rejects_missing_images(self):
        row = self.base_row()
        row["Посилання_зображення"] = ""

        with self.assertRaises(ValueError):
            validate_rows([row])

    def test_rejects_non_numeric_variant_group_id(self):
        row = self.base_row()
        row["ID_групи_різновидів"] = "modniy-1"

        with self.assertRaises(ValueError):
            validate_rows([row])

    def test_rejects_forbidden_service_code(self):
        row = self.base_row()
        row["Назва_позиції"] = "Купальник Fuba 25122 48"

        with self.assertRaises(ValueError):
            validate_rows([row])


if __name__ == "__main__":
    unittest.main()
