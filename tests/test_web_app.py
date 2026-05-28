import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import web_app
from src.app_service import GeneratedFile


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(web_app.app)

    def test_index_returns_form(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="product_url"', response.text)
        self.assertIn('name="color_id"', response.text)
        self.assertIn("data-message", response.text)
        self.assertIn("X-Requested-With", response.text)
        self.assertIn("clearGeneratedFormFields", response.text)
        self.assertIn('form.elements.namedItem("product_url").value = ""', response.text)
        self.assertIn('form.elements.namedItem("color_id").value = ""', response.text)

    def test_invalid_generate_returns_400_with_html_friendly_message(self):
        response = self.client.post(
            "/generate",
            data={"product_url": "https://example.com/product.html", "color_id": "65"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Вставте посилання на товар з modniy-shopping.com.ua.", response.text)

    def test_invalid_fetch_generate_returns_400_json_error(self):
        response = self.client.post(
            "/generate",
            data={"product_url": "https://example.com/product.html", "color_id": "65"},
            headers={"X-Requested-With": "fetch"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertEqual(response.json(), {"error": "Вставте посилання на товар з modniy-shopping.com.ua."})

    def test_valid_generate_returns_xlsx_download(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "import-products-3064637917.xlsx"
            output_path.write_bytes(b"xlsx-data")

            with patch(
                "web_app.generate_from_user_input",
                return_value=GeneratedFile(path=output_path, filename=output_path.name),
            ) as service:
                response = self.client.post(
                    "/generate",
                    data={
                        "product_url": "https://modniy-shopping.com.ua/ua/p3064637917-product.html",
                        "color_id": "65",
                    },
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], web_app.XLSX_MEDIA_TYPE)
        self.assertIn("attachment;", response.headers["content-disposition"])
        self.assertEqual(response.content, b"xlsx-data")
        service.assert_called_once()


if __name__ == "__main__":
    unittest.main()
