import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.parser.modniy_shopping import parse_product_html


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class ModniyShoppingParserTests(unittest.TestCase):
    def parse_fixture(self, product_id: str):
        html = (FIXTURES / f"modniy_{product_id}.html").read_text(encoding="utf-8")
        url = f"https://modniy-shopping.com.ua/ua/p{product_id}-product.html"
        return parse_product_html(html, url)

    def test_parses_horizontal_size_table(self):
        product = self.parse_fixture("3064637917")

        self.assertEqual(product.product_id, "3064637917")
        self.assertEqual(product.sku, "25122")
        self.assertEqual(product.brand, "Fuba")
        self.assertEqual(product.price, "763.00")
        self.assertEqual([item.ua_size for item in product.size_table], ["48", "50", "52", "54", "56"])
        self.assertEqual([item.intl_size for item in product.size_table], ["L", "XL", "2XL", "3XL", "4XL"])
        self.assertEqual(product.size_table[0].label_size, "48")
        self.assertEqual(product.size_table[0].hips, "101-104")
        self.assertEqual(product.size_table[0].cup, "Між 2B-3С")
        self.assertGreaterEqual(len(product.images), 5)

    def test_parses_vertical_size_table(self):
        product = self.parse_fixture("2999460479")

        self.assertEqual([item.ua_size for item in product.size_table], ["60", "62", "64", "66", "68"])
        self.assertEqual(product.size_table[0].label_size, "66")
        self.assertEqual(product.size_table[0].hips, "128-132")
        self.assertEqual(product.size_table[0].cup, "3С-5Е")

    def test_falls_back_to_sizes_from_title_when_table_missing(self):
        product = self.parse_fixture("3058795661")

        self.assertEqual([item.ua_size for item in product.size_table], ["48", "50", "52", "54", "56"])
        self.assertTrue(all(item.label_size is None for item in product.size_table))
        self.assertTrue(all(item.hips is None for item in product.size_table))
        self.assertTrue(all(item.cup is None for item in product.size_table))

    def test_parses_all_reference_fixture_sizes(self):
        expected = {
            "3064639273": ["46", "48", "50", "52", "54"],
            "3028043687": ["52", "54", "56", "58", "60"],
        }

        for product_id, sizes in expected.items():
            with self.subTest(product_id=product_id):
                product = self.parse_fixture(product_id)
                self.assertEqual([item.ua_size for item in product.size_table], sizes)


if __name__ == "__main__":
    unittest.main()
