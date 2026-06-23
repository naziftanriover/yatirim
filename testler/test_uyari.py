"""Uyarı koşulu testleri (ÖNCE yazıldı)."""

import unittest
from decimal import Decimal

from yatirim.uyari.kosul import fiyat_uyarisi, rsi_uyarisi, UyariSonucu


class FiyatUyarisiTest(unittest.TestCase):

    def test_ust_hedef_asilinca_tetiklenir(self):
        s = fiyat_uyarisi(Decimal("105"), Decimal("100"), yon="ust")
        self.assertIsInstance(s, UyariSonucu)
        self.assertTrue(s.tetiklendi)

    def test_ust_hedef_asilmazsa_tetiklenmez(self):
        s = fiyat_uyarisi(Decimal("95"), Decimal("100"), yon="ust")
        self.assertFalse(s.tetiklendi)

    def test_alt_hedef_altina_dusunce_tetiklenir(self):
        s = fiyat_uyarisi(Decimal("95"), Decimal("100"), yon="alt")
        self.assertTrue(s.tetiklendi)

    def test_gecersiz_yon_hata(self):
        with self.assertRaises(ValueError):
            fiyat_uyarisi(Decimal("100"), Decimal("100"), yon="sag")


class RsiUyarisiTest(unittest.TestCase):

    def test_asiri_alim(self):
        s = rsi_uyarisi(Decimal("75"))
        self.assertTrue(s.tetiklendi)
        self.assertIn("aşırı alım", s.mesaj.lower())

    def test_asiri_satim(self):
        s = rsi_uyarisi(Decimal("25"))
        self.assertTrue(s.tetiklendi)
        self.assertIn("aşırı satım", s.mesaj.lower())

    def test_normal_bolge_tetiklenmez(self):
        s = rsi_uyarisi(Decimal("50"))
        self.assertFalse(s.tetiklendi)


if __name__ == "__main__":
    unittest.main()
