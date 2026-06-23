"""Zarar-kes (stop-loss) kuralının testleri (ÖNCE yazıldı).

Kural:
  - Her işlemde stop-loss ZORUNLU (yoksa işlem uygun değil).
  - Stop doğru tarafta olmalı:
      * uzun (alım)  pozisyonda stop, giriş fiyatının ALTINDA olmalı.
      * kısa (satış) pozisyonda stop, giriş fiyatının ÜSTÜNDE olmalı.
  - Riske atılan para = mesafe x adet.

Çalıştırmak için proje kökünde:
    python3 -m unittest testler.test_stop -v
"""

import unittest
from decimal import Decimal

from yatirim.risk.stop import zarar_kes_kontrol, ZararKesSonucu


class ZararKesKontrolTest(unittest.TestCase):

    def test_uzun_pozisyon_gecerli_stop(self):
        # 100'den al, stop 90, 10 adet -> risk = (100-90)*10 = 100
        s = zarar_kes_kontrol(
            giris_fiyati=Decimal("100"),
            stop_fiyati=Decimal("90"),
            adet=Decimal("10"),
            yon="uzun",
        )
        self.assertIsInstance(s, ZararKesSonucu)
        self.assertTrue(s.uygun)
        self.assertEqual(s.ihlaller, [])
        self.assertEqual(s.riske_atilan, Decimal("100"))

    def test_stop_yoksa_uygun_degil(self):
        # Stop verilmedi (None) -> zorunluluk ihlali.
        s = zarar_kes_kontrol(Decimal("100"), None, Decimal("10"), yon="uzun")
        self.assertFalse(s.uygun)
        self.assertEqual(len(s.ihlaller), 1)
        self.assertIn("stop", s.ihlaller[0].lower())

    def test_uzun_pozisyonda_stop_yanlis_tarafta(self):
        # Uzun pozisyonda stop girişin üstünde olamaz.
        s = zarar_kes_kontrol(Decimal("100"), Decimal("110"), Decimal("10"), yon="uzun")
        self.assertFalse(s.uygun)
        self.assertIn("altında", s.ihlaller[0].lower())

    def test_kisa_pozisyon_gecerli_stop(self):
        # Kısa (satış): 100'den sat, stop 110, 5 adet -> risk = (110-100)*5 = 50
        s = zarar_kes_kontrol(Decimal("100"), Decimal("110"), Decimal("5"), yon="kisa")
        self.assertTrue(s.uygun)
        self.assertEqual(s.riske_atilan, Decimal("50"))

    def test_kisa_pozisyonda_stop_yanlis_tarafta(self):
        s = zarar_kes_kontrol(Decimal("100"), Decimal("90"), Decimal("5"), yon="kisa")
        self.assertFalse(s.uygun)
        self.assertIn("üstünde", s.ihlaller[0].lower())

    def test_kurus_hassasiyeti(self):
        # 1.50'den al, stop 1.45, 100 adet -> risk = 0.05*100 = 5.00
        s = zarar_kes_kontrol(Decimal("1.50"), Decimal("1.45"), Decimal("100"), yon="uzun")
        self.assertTrue(s.uygun)
        self.assertEqual(s.riske_atilan, Decimal("5.00"))

    def test_negatif_giris_hata(self):
        with self.assertRaises(ValueError):
            zarar_kes_kontrol(Decimal("-1"), Decimal("0.5"), Decimal("10"), yon="uzun")

    def test_adet_sifir_hata(self):
        with self.assertRaises(ValueError):
            zarar_kes_kontrol(Decimal("100"), Decimal("90"), Decimal("0"), yon="uzun")

    def test_gecersiz_yon_hata(self):
        with self.assertRaises(ValueError):
            zarar_kes_kontrol(Decimal("100"), Decimal("90"), Decimal("10"), yon="yan")


if __name__ == "__main__":
    unittest.main()
