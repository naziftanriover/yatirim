"""Canlı adaptörün internet GEREKTİRMEYEN yardımcılarının testleri.

Not: fiyat_gecmisi/temel_veri internet ister; onlar burada test edilmez,
kendi bilgisayarında çalışır.
"""

import unittest
from decimal import Decimal

from yatirim.veri.canli import bist_sembol, _dec


class BistSembolTest(unittest.TestCase):

    def test_ek_ekler(self):
        self.assertEqual(bist_sembol("THYAO"), "THYAO.IS")

    def test_kucuk_harfi_buyutur(self):
        self.assertEqual(bist_sembol("thyao"), "THYAO.IS")

    def test_zaten_varsa_tekrar_eklemez(self):
        self.assertEqual(bist_sembol("ASELS.IS"), "ASELS.IS")


class DecCevirTest(unittest.TestCase):

    def test_none_none_doner(self):
        self.assertIsNone(_dec(None))

    def test_sayi_decimal_olur(self):
        self.assertEqual(_dec("12.5"), Decimal("12.5"))
        self.assertEqual(_dec(3), Decimal("3"))

    def test_nan_none_olur(self):
        self.assertIsNone(_dec(float("nan")))


if __name__ == "__main__":
    unittest.main()
