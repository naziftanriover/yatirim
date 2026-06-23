"""Ek teknik gösterge testleri (ÖNCE yazıldı): EMA, MACD, Bollinger, Stokastik.

Test değerleri elle doğrulanabilecek şekilde (temiz sayılarla) seçildi.
"""

import unittest
from decimal import Decimal

from yatirim.teknik.ema import ussel_hareketli_ortalama
from yatirim.teknik.macd import macd, MacdSonucu
from yatirim.teknik.bollinger import bollinger_bantlari, BollingerSonucu
from yatirim.teknik.stokastik import stokastik_k


class EmaTest(unittest.TestCase):

    def test_ema_periyot_uc(self):
        # periyot 3 -> k = 2/4 = 0.5 (temiz). prices [2,4,6,8,10]
        # seed = SMA(2,4,6)=4; sonra: 0.5*fiyat + 0.5*onceki
        sonuc = ussel_hareketli_ortalama(
            [Decimal(n) for n in [2, 4, 6, 8, 10]], 3
        )
        self.assertEqual(sonuc, [Decimal("4"), Decimal("6"), Decimal("8")])

    def test_yetersiz_veri_hata(self):
        with self.assertRaises(ValueError):
            ussel_hareketli_ortalama([Decimal("1")], 3)


class MacdTest(unittest.TestCase):

    def test_sabit_seride_sifir(self):
        # Tüm fiyatlar eşitse MACD, sinyal ve histogram hep 0 olmalı.
        fiyatlar = [Decimal("5")] * 40
        s = macd(fiyatlar)
        self.assertIsInstance(s, MacdSonucu)
        self.assertTrue(all(v == 0 for v in s.macd_cizgi))
        self.assertTrue(all(v == 0 for v in s.sinyal))
        self.assertTrue(all(v == 0 for v in s.histogram))

    def test_yetersiz_veri_hata(self):
        with self.assertRaises(ValueError):
            macd([Decimal("5")] * 10)


class BollingerTest(unittest.TestCase):

    def test_bollinger_periyot_iki(self):
        # periyot 2, k=2. prices [1,3,5]
        # pencere [1,3]: orta 2, std 1 -> ust 4, alt 0
        # pencere [3,5]: orta 4, std 1 -> ust 6, alt 2
        s = bollinger_bantlari([Decimal("1"), Decimal("3"), Decimal("5")], periyot=2, k=Decimal("2"))
        self.assertIsInstance(s, BollingerSonucu)
        self.assertEqual(s.orta, [Decimal("2"), Decimal("4")])
        self.assertEqual(s.ust, [Decimal("4"), Decimal("6")])
        self.assertEqual(s.alt, [Decimal("0"), Decimal("2")])

    def test_yetersiz_veri_hata(self):
        with self.assertRaises(ValueError):
            bollinger_bantlari([Decimal("1")], periyot=2)


class StokastikTest(unittest.TestCase):

    def test_stokastik_k(self):
        # [10,12,8,11,9], periyot 4
        # pencere1 [10,12,8,11]: low8 high12 close11 -> (11-8)/(12-8)*100 = 75
        # pencere2 [12,8,11,9]:  low8 high12 close9  -> (9-8)/(12-8)*100 = 25
        sonuc = stokastik_k([Decimal(n) for n in [10, 12, 8, 11, 9]], periyot=4)
        self.assertEqual(sonuc, [Decimal("75.00"), Decimal("25.00")])

    def test_yetersiz_veri_hata(self):
        with self.assertRaises(ValueError):
            stokastik_k([Decimal("10")], periyot=4)


if __name__ == "__main__":
    unittest.main()
