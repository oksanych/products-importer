import unittest

from src.normalizer.price import PRICE_PARAMETER_ERROR, validate_import_price


class PriceNormalizerTests(unittest.TestCase):
    def test_accepts_whole_uah_price_values(self):
        cases = {
            "1000": 1000,
            "1000.00": 1000,
            "1000,00": 1000,
            " 1000 ": 1000,
        }

        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                self.assertEqual(validate_import_price(raw_value), expected)

    def test_rejects_invalid_import_prices_with_clear_message(self):
        for raw_value in [None, "", "0", "-1", "abc", "999.50", "10000000000"]:
            with self.subTest(raw_value=raw_value):
                with self.assertRaises(ValueError) as context:
                    validate_import_price(raw_value)

                self.assertEqual(str(context.exception), PRICE_PARAMETER_ERROR)


if __name__ == "__main__":
    unittest.main()
