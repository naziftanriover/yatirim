"""Kağıt cüzdan testleri (ÖNCE yazıldı). Sahte parayla al-sat; gerçek para YOK."""

import unittest
from decimal import Decimal

from yatirim.kagit.cuzdan import KagitCuzdan


class KagitCuzdanTest(unittest.TestCase):

    def test_baslangic(self):
        c = KagitCuzdan(Decimal("1000"))
        self.assertEqual(c.nakit, Decimal("1000"))
        self.assertEqual(c.pozisyonlar, {})

    def test_al_nakit_azaltir_pozisyon_ekler(self):
        c = KagitCuzdan(Decimal("1000"))
        c.al("AAPL", fiyat=Decimal("100"), adet=Decimal("3"))
        self.assertEqual(c.nakit, Decimal("700"))
        self.assertEqual(c.pozisyonlar["AAPL"], Decimal("3"))

    def test_yetersiz_nakitle_al_hata(self):
        c = KagitCuzdan(Decimal("100"))
        with self.assertRaises(ValueError):
            c.al("AAPL", Decimal("100"), Decimal("2"))  # 200 > 100

    def test_sat_nakit_ekler_pozisyon_azaltir(self):
        c = KagitCuzdan(Decimal("1000"))
        c.al("AAPL", Decimal("100"), Decimal("3"))
        c.sat("AAPL", Decimal("120"), Decimal("2"))
        self.assertEqual(c.nakit, Decimal("940"))          # 700 + 240
        self.assertEqual(c.pozisyonlar["AAPL"], Decimal("1"))

    def test_elde_olmayani_satamaz(self):
        c = KagitCuzdan(Decimal("1000"))
        with self.assertRaises(ValueError):
            c.sat("AAPL", Decimal("100"), Decimal("1"))

    def test_tamami_satilinca_pozisyon_silinir(self):
        c = KagitCuzdan(Decimal("1000"))
        c.al("AAPL", Decimal("100"), Decimal("2"))
        c.sat("AAPL", Decimal("110"), Decimal("2"))
        self.assertNotIn("AAPL", c.pozisyonlar)

    def test_toplam_deger_ve_getiri(self):
        c = KagitCuzdan(Decimal("1000"))
        c.al("AAPL", Decimal("100"), Decimal("5"))   # nakit 500, 5 adet
        # AAPL 120 olunca: 500 + 5*120 = 1100
        deger = c.toplam_deger({"AAPL": Decimal("120")})
        self.assertEqual(deger, Decimal("1100"))
        self.assertEqual(c.getiri_yuzde({"AAPL": Decimal("120")}), Decimal("10.00"))


if __name__ == "__main__":
    unittest.main()
