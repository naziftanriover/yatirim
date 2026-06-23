"""Temel analiz oran testleri (ÖNCE yazıldı)."""

import unittest
from decimal import Decimal

from yatirim.temel.oranlar import fiyat_kazanc, borc_ozkaynak, piyasa_defter


class FiyatKazancTest(unittest.TestCase):

    def test_fk_hesabi(self):
        # Fiyat 100, hisse başı kazanç 5 -> F/K = 20
        self.assertEqual(fiyat_kazanc(Decimal("100"), Decimal("5")), Decimal("20.00"))

    def test_negatif_kazanc_hata(self):
        # Zarar eden şirkette F/K anlamsız -> hata
        with self.assertRaises(ValueError):
            fiyat_kazanc(Decimal("100"), Decimal("-2"))

    def test_sifir_kazanc_hata(self):
        with self.assertRaises(ValueError):
            fiyat_kazanc(Decimal("100"), Decimal("0"))


class BorcOzkaynakTest(unittest.TestCase):

    def test_borc_ozkaynak_hesabi(self):
        # Borç 200, özkaynak 100 -> 2.0
        self.assertEqual(borc_ozkaynak(Decimal("200"), Decimal("100")), Decimal("2.00"))

    def test_borcsuz_sirket(self):
        self.assertEqual(borc_ozkaynak(Decimal("0"), Decimal("100")), Decimal("0.00"))

    def test_ozkaynak_sifir_hata(self):
        with self.assertRaises(ValueError):
            borc_ozkaynak(Decimal("200"), Decimal("0"))


class PiyasaDefterTest(unittest.TestCase):

    def test_pddd_hesabi(self):
        # Fiyat 50, hisse başı defter değeri 25 -> 2.0
        self.assertEqual(piyasa_defter(Decimal("50"), Decimal("25")), Decimal("2.00"))

    def test_defter_negatif_hata(self):
        with self.assertRaises(ValueError):
            piyasa_defter(Decimal("50"), Decimal("-1"))


if __name__ == "__main__":
    unittest.main()
