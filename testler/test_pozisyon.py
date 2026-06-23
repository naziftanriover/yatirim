"""Pozisyon büyüklüğü kuralının testleri (ÖNCE bu yazıldı, sonra kod).

Çalıştırmak için proje kökünde:
    python3 -m unittest testler.test_pozisyon -v
"""

import unittest
from decimal import Decimal

# Henüz var olmayan modülü çağırıyoruz; bu yüzden test ilk başta KIRMIZI olacak.
from yatirim.risk.pozisyon import izin_verilen_max_tutar


class IzinVerilenMaxTutarTest(unittest.TestCase):

    def test_basit_yuzde_hesabi(self):
        # 100.000 paranın %2'si = 2.000
        sonuc = izin_verilen_max_tutar(Decimal("100000"), Decimal("2"))
        self.assertEqual(sonuc, Decimal("2000"))

    def test_kucuk_yuzde_kurus_hassasiyeti(self):
        # 10.000 paranın %1.5'i = 150 (Decimal ile tam, yuvarlama hatası YOK)
        sonuc = izin_verilen_max_tutar(Decimal("10000"), Decimal("1.5"))
        self.assertEqual(sonuc, Decimal("150"))

    def test_negatif_sermaye_reddedilir(self):
        # Negatif para mantıksız; fonksiyon hata vermeli (bizi korur).
        with self.assertRaises(ValueError):
            izin_verilen_max_tutar(Decimal("-100"), Decimal("2"))

    def test_sifir_yuzde_reddedilir(self):
        # %0 anlamsız bir kural; reddedilmeli.
        with self.assertRaises(ValueError):
            izin_verilen_max_tutar(Decimal("100000"), Decimal("0"))

    def test_yuzde_yuzden_buyuk_reddedilir(self):
        # %100'den büyük yüzde (tüm paradan fazlası) reddedilmeli.
        with self.assertRaises(ValueError):
            izin_verilen_max_tutar(Decimal("100000"), Decimal("150"))

    def test_yuzde_tam_yuz_kabul_edilir(self):
        # %100 sınırda ama geçerli: tüm para tek işleme (sınır durumu).
        sonuc = izin_verilen_max_tutar(Decimal("100000"), Decimal("100"))
        self.assertEqual(sonuc, Decimal("100000"))


if __name__ == "__main__":
    unittest.main()
