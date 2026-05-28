import unittest
from pathlib import Path

from src.app_service import (
    GENERATION_FAILED_MESSAGE,
    INVALID_COLOR_ID_MESSAGE,
    WRONG_DOMAIN_MESSAGE,
    GenerationError,
    InputValidationError,
    generate_from_user_input,
)


class AppServiceTests(unittest.TestCase):
    def test_rejects_wrong_domain(self):
        with self.assertRaises(InputValidationError) as context:
            generate_from_user_input("https://example.com/product.html", "65")

        self.assertEqual(context.exception.user_message, WRONG_DOMAIN_MESSAGE)

    def test_rejects_non_https_url(self):
        with self.assertRaises(InputValidationError) as context:
            generate_from_user_input("http://modniy-shopping.com.ua/ua/p3064637917-product.html", "65")

        self.assertEqual(context.exception.user_message, WRONG_DOMAIN_MESSAGE)

    def test_rejects_invalid_color_id(self):
        with self.assertRaises(InputValidationError) as context:
            generate_from_user_input("https://modniy-shopping.com.ua/ua/p3064637917-product.html", "5")

        self.assertEqual(context.exception.user_message, INVALID_COLOR_ID_MESSAGE)

    def test_trims_input_before_generation(self):
        calls = []

        def fake_generator(product_url, template_path, output_dir, *, color_id):
            calls.append((product_url, template_path, output_dir, color_id))
            return str(Path(output_dir) / "import-products-3064637917.xlsx")

        result = generate_from_user_input(
            "  https://modniy-shopping.com.ua/ua/p3064637917-product.html  ",
            " 65 ",
            output_root="output-test",
            generator=fake_generator,
        )

        self.assertEqual(calls[0][0], "https://modniy-shopping.com.ua/ua/p3064637917-product.html")
        self.assertEqual(calls[0][3], "65")
        self.assertEqual(result.filename, "import-products-3064637917.xlsx")

    def test_returns_generated_file_metadata_with_unique_output_dir(self):
        output_dirs = []

        def fake_generator(product_url, template_path, output_dir, *, color_id):
            output_dirs.append(output_dir)
            return str(Path(output_dir) / "import-products-3064637917.xlsx")

        first = generate_from_user_input(
            "https://modniy-shopping.com.ua/ua/p3064637917-product.html",
            "65",
            output_root="output-test",
            generator=fake_generator,
        )
        second = generate_from_user_input(
            "https://modniy-shopping.com.ua/ua/p3064637917-product.html",
            "65",
            output_root="output-test",
            generator=fake_generator,
        )

        self.assertNotEqual(output_dirs[0], output_dirs[1])
        self.assertEqual(first.filename, "import-products-3064637917.xlsx")
        self.assertEqual(second.filename, "import-products-3064637917.xlsx")

    def test_wraps_generation_failure_with_friendly_message(self):
        def failing_generator(product_url, template_path, output_dir, *, color_id):
            raise RuntimeError("network failed")

        with self.assertLogs("src.app_service", level="ERROR"):
            with self.assertRaises(GenerationError) as context:
                generate_from_user_input(
                    "https://modniy-shopping.com.ua/ua/p3064637917-product.html",
                    "65",
                    generator=failing_generator,
                )

        self.assertEqual(context.exception.user_message, GENERATION_FAILED_MESSAGE)


if __name__ == "__main__":
    unittest.main()
