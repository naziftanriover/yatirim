"""Teknik gösterge testleri (ÖNCE yazıldı): SMA ve RSI."""

import unittest
from decimal import Decimal

from yatirim.teknik.hareketli_ortalama import basit_hareketli_ortalama
from yatirim.teknik.rsi import rsi


class HareketliOrtalamaTest(unittest.TestCase):

    def test_basit_sma(self):
        # [10,20,30,40], periyot 2 -> [15,25,35]
        sonuc = basit_hareketli_ortalama(
            [Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40")], 2
        )
        self.assertEqual(sonuc, [Decimal("15"), Decimal("25"), Decimal("35")])

    def test_periyot_tum_listeye_esit(self):
        sonuc = basit_hareketli_ortalama([Decimal("10"), Decimal("20")], 2)
        self.assertEqual(sonuc, [Decimal("15")])

    def test_yetersiz_veri_hata(self):
        with self.assertRaises(ValueError):
            basit_hareketli_ortalama([Decimal("10")], 2)

    def test_periyot_sifir_hata(self):
        with self.assertRaises(ValueError):
            basit_hareketli_ortalama([Decimal("10"), Decimal("20")], 0)


class RsiTest(unittest.TestCase):

    def test_hep_yukselen_rsi_yuz(self):
        # Sürekli artış -> hiç kayıp yok -> RSI 100
        sonuc = rsi([Decimal(n) for n in [1, 2, 3, 4, 5]], periyot=4)
        self.assertEqual(sonuc, Decimal("100.00"))

    def test_hep_dusen_rsi_sifir(self):
        sonuc = rsi([Decimal(n) for n in [5, 4, 3, 2, 1]], periyot=4)
        self.assertEqual(sonuc, Decimal("0.00"))

    def test_dengeli_rsi_elli(self):
        # +1,-1,+1,-1 -> ortalama kazanç = ortalama kayıp -> RSI 50
        sonuc = rsi([Decimal(n) for n in [10, 11, 10, 11, 10]], periyot=4)
        self.assertEqual(sonuc, Decimal("50.00"))

    def test_yetersiz_veri_hata(self):
        # periyot 4 için en az 5 fiyat lazım
        with self.assertRaises(ValueError):
            rsi([Decimal(n) for n in [1, 2, 3, 4]], periyot=4)


if __name__ == "__main__":
    unittest.main()
