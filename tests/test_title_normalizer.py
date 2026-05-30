import unittest

from src.normalizer.title import (
    PositionTitleValidationError,
    position_title_for_size,
    position_title_ukr_for_size,
)


class TitleNormalizerTests(unittest.TestCase):
    def test_accepts_position_title_when_appended_size_fits_prom_limit(self):
        self.assertEqual(position_title_for_size("А" * 107, "48"), f"{'А' * 107} 48")

    def test_rejects_position_title_when_appended_size_exceeds_prom_limit(self):
        with self.assertRaises(PositionTitleValidationError):
            position_title_for_size("А" * 108, "48")

    def test_accepts_ukrainian_position_title_when_appended_size_fits_prom_limit(self):
        self.assertEqual(position_title_ukr_for_size("А" * 127, "48"), f"{'А' * 127} 48")

    def test_rejects_ukrainian_position_title_when_appended_size_exceeds_prom_limit(self):
        with self.assertRaises(PositionTitleValidationError):
            position_title_ukr_for_size("А" * 128, "48")


if __name__ == "__main__":
    unittest.main()
