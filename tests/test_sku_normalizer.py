import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.normalizer.sku import format_product_code, validate_color_id


class SkuNormalizerTests(unittest.TestCase):
    def test_formats_simple_sku_with_ms_prefix_and_color_id(self):
        self.assertEqual(format_product_code("3903", "65"), "MS390365")

    def test_strips_trailing_numeric_supplier_suffix(self):
        self.assertEqual(format_product_code("58800-25", "45"), "MS5880045")

    def test_preserves_leading_zero_color_id(self):
        self.assertEqual(format_product_code("58800-25", "05"), "MS5880005")

    def test_does_not_strip_non_trailing_or_non_numeric_hyphen_parts(self):
        self.assertEqual(format_product_code("AB-58800-X", "65"), "MSAB-58800-X65")
        self.assertEqual(format_product_code("58800-RED", "65"), "MS58800-RED65")

    def test_accepts_exactly_two_digit_color_ids(self):
        self.assertEqual(validate_color_id("65"), "65")
        self.assertEqual(validate_color_id("05"), "05")

    def test_rejects_invalid_color_ids_with_clear_message(self):
        for value in ["5", "005", "ab", "", None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Check color parameter"):
                    validate_color_id(value)


if __name__ == "__main__":
    unittest.main()
