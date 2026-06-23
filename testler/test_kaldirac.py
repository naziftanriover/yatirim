"""Kaldıraç/margin kuralının testleri (ÖNCE yazıldı).

Kural (Nazif'in seçimi):
  - Kaldıraç serbest AMA kendi koyduğun para (teminat) ana paranın en fazla %20'si.
  - En fazla 5x kaldıraç.

Çalıştırmak için proje kökünde:
    python3 -m unittest testler.test_kaldirac -v
"""

import unittest
from decimal import Decimal

from yatirim.risk.kaldirac import kaldirac_kontrol, KaldiracSonucu


class KaldiracKontrolTest(unittest.TestCase):

    def test_uygun_islem(self):
        # Teminat %20 (sınırda), kaldıraç 5x (sınırda) -> uygun.
        s = kaldirac_kontrol(
            toplam_sermaye=Decimal("100000"),
            teminat=Decimal("20000"),
            kaldirac_orani=Decimal("5"),
        )
        self.assertIsInstance(s, KaldiracSonucu)
        self.assertTrue(s.uygun)
        self.assertEqual(s.ihlaller, [])
        # Maruziyet = teminat x kaldıraç = 20000 x 5 = 100000
        self.assertEqual(s.maruziyet, Decimal("100000"))

    def test_teminat_yuzde_yirmiyi_gecemez(self):
        # Teminat %25 -> ihlal, uygun değil.
        s = kaldirac_kontrol(Decimal("100000"), Decimal("25000"), Decimal("3"))
        self.assertFalse(s.uygun)
        self.assertEqual(len(s.ihlaller), 1)
        self.assertIn("teminat", s.ihlaller[0].lower())

    def test_kaldirac_bes_kati_gecemez(self):
        # 6x -> ihlal.
        s = kaldirac_kontrol(Decimal("100000"), Decimal("10000"), Decimal("6"))
        self.assertFalse(s.uygun)
        self.assertEqual(len(s.ihlaller), 1)
        self.assertIn("kaldıraç", s.ihlaller[0].lower())

    def test_iki_ihlal_birden(self):
        # Hem teminat %30 hem kaldıraç 8x -> iki ihlal.
        s = kaldirac_kontrol(Decimal("100000"), Decimal("30000"), Decimal("8"))
        self.assertFalse(s.uygun)
        self.assertEqual(len(s.ihlaller), 2)

    def test_kaldiracsiz_islem_uygun(self):
        # Kaldıraç 1x (borç yok), teminat %2 -> uygun, maruziyet = teminat.
        s = kaldirac_kontrol(Decimal("100000"), Decimal("2000"), Decimal("1"))
        self.assertTrue(s.uygun)
        self.assertEqual(s.maruziyet, Decimal("2000"))

    def test_negatif_teminat_hata(self):
        with self.assertRaises(ValueError):
            kaldirac_kontrol(Decimal("100000"), Decimal("-1"), Decimal("2"))

    def test_kaldirac_birden_kucuk_hata(self):
        # 1'in altı (örn. 0.5x) anlamsız; hata vermeli.
        with self.assertRaises(ValueError):
            kaldirac_kontrol(Decimal("100000"), Decimal("1000"), Decimal("0.5"))

    def test_sermaye_sifir_veya_negatif_hata(self):
        with self.assertRaises(ValueError):
            kaldirac_kontrol(Decimal("0"), Decimal("1000"), Decimal("2"))


if __name__ == "__main__":
    unittest.main()
