import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.product import Product, SizeVariant
from src.normalizer.text import build_description, title_for_size


class TextNormalizerTests(unittest.TestCase):
    def test_build_description_includes_centered_product_images_before_size_table(self):
        product = Product(
            url="https://modniy-shopping.com.ua/ua/p1-product.html",
            product_id="1",
            name="Злитий купальник Fuba 48 50 розмір",
            sku="25122",
            brand="Fuba",
            price="763.00",
            description="Жіночий купальник для басейну.",
            images=[
                "https://images.prom.ua/610000001_w640_h640_product-0.jpg",
                "https://images.prom.ua/610000002_w640_h640_product-1.jpg?fresh=1",
            ],
            size_table=[SizeVariant(ua_size="48"), SizeVariant(ua_size="50")],
        )

        description = build_description(product, "uk")

        self.assertEqual(description.count("<img"), 2)
        self.assertEqual(description.count('style="text-align:center"'), 2)
        self.assertIn(
            '<p style="text-align:center"><img alt="610000001_w640_h640_product-0.jpg" '
            'src="https://images.prom.ua/610000001_w640_h640_product-0.jpg" /></p>',
            description,
        )
        self.assertIn(
            '<p style="text-align:center"><img alt="610000002_w640_h640_product-1.jpg" '
            'src="https://images.prom.ua/610000002_w640_h640_product-1.jpg?fresh=1" /></p>',
            description,
        )
        self.assertLess(description.index("<img"), description.index("<table>"))

    def test_removes_visible_service_code_when_structured_brand_differs(self):
        product = Product(
            url="https://modniy-shopping.com.ua/ua/p3058885266-product.html",
            product_id="3058885266",
            name="Купальник цілисний Fuba 26069 зелений 52 54 56 58 60 розмір",
            sku="26069",
            brand="Z. Five",
            price="763.00",
            description="Купальник Fuba 26069 великих розмірів.",
            images=["https://images.prom.ua/610000001_w640_h640_product-0.jpg"],
            size_table=[SizeVariant(ua_size="52")],
        )

        title = title_for_size(product, "52", "uk")
        description = build_description(product, "uk")

        self.assertEqual(title, "Купальник цілисний зелений 52")
        self.assertNotIn("Fuba 26069", description)


if __name__ == "__main__":
    unittest.main()
