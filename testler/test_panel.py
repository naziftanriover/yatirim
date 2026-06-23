"""Tarama panosu sıralama testleri (ÖNCE yazıldı).

Ağ (tarama_yap) burada test edilmez; saf sıralama (sirala) test edilir.
"""

import unittest

from decimal import Decimal

from yatirim.tarama.panel import sirala, TaramaSatiri, gunluk_degisim_yuzde


class GunlukDegisimTest(unittest.TestCase):

    def test_yukselis(self):
        self.assertEqual(
            gunluk_degisim_yuzde([Decimal("100"), Decimal("110")]), Decimal("10.00"))

    def test_dusus(self):
        self.assertEqual(
            gunluk_degisim_yuzde([Decimal("100"), Decimal("90")]), Decimal("-10.00"))

    def test_yetersiz_veri_none(self):
        self.assertIsNone(gunluk_degisim_yuzde([Decimal("100")]))


class SiralaTest(unittest.TestCase):

    def test_skora_gore_azalan(self):
        satirlar = [
            TaramaSatiri(sembol="A", yon="Nötr", skor=1),
            TaramaSatiri(sembol="B", yon="Olumlu", skor=5),
            TaramaSatiri(sembol="C", yon="Zayıf", skor=-3),
        ]
        sirali = sirala(satirlar)
        self.assertEqual([s.sembol for s in sirali], ["B", "A", "C"])

    def test_hatalilar_sona_gider(self):
        satirlar = [
            TaramaSatiri(sembol="X", yon="-", skor=0, hata="veri yok"),
            TaramaSatiri(sembol="Y", yon="Olumlu", skor=4),
        ]
        sirali = sirala(satirlar)
        self.assertEqual([s.sembol for s in sirali], ["Y", "X"])

    def test_bos_liste(self):
        self.assertEqual(sirala([]), [])


if __name__ == "__main__":
    unittest.main()
