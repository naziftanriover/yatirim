"""Backtest testleri (ÖNCE yazıldı): icra motoru + SMA kesişim sinyalleri."""

import unittest
from decimal import Decimal

from yatirim.backtest.calistir import (
    backtest,
    sma_kesisim_sinyalleri,
    BacktestSonucu,
)


class BacktestIcraTest(unittest.TestCase):

    def test_al_sonra_sat_kar(self):
        # 10'dan al, 20'den sat -> 1000 TL -> 2000 TL, %100 getiri
        s = backtest(
            fiyatlar=[Decimal("10"), Decimal("20")],
            sinyaller=["AL", "SAT"],
            baslangic_nakit=Decimal("1000"),
        )
        self.assertIsInstance(s, BacktestSonucu)
        self.assertEqual(s.son_deger, Decimal("2000"))
        self.assertEqual(s.getiri_yuzde, Decimal("100.00"))
        self.assertEqual(s.islem_sayisi, 2)

    def test_al_sonra_sat_zarar(self):
        # 10'dan al, 5'ten sat -> 1000 -> 500, -%50
        s = backtest([Decimal("10"), Decimal("5")], ["AL", "SAT"], Decimal("1000"))
        self.assertEqual(s.son_deger, Decimal("500"))
        self.assertEqual(s.getiri_yuzde, Decimal("-50.00"))

    def test_al_tut_sona_kadar(self):
        # 10'dan al, tut; son fiyat 12 -> 1200, %20, 1 işlem
        s = backtest(
            [Decimal("10"), Decimal("11"), Decimal("12")],
            ["AL", "BEKLE", "BEKLE"],
            Decimal("1000"),
        )
        self.assertEqual(s.son_deger, Decimal("1200"))
        self.assertEqual(s.getiri_yuzde, Decimal("20.00"))
        self.assertEqual(s.islem_sayisi, 1)

    def test_uzunluk_uyusmazligi_hata(self):
        with self.assertRaises(ValueError):
            backtest([Decimal("10")], ["AL", "SAT"], Decimal("1000"))

    def test_gecersiz_sinyal_hata(self):
        with self.assertRaises(ValueError):
            backtest([Decimal("10")], ["ZIPLA"], Decimal("1000"))

    def test_baslangic_nakit_sifir_hata(self):
        with self.assertRaises(ValueError):
            backtest([Decimal("10")], ["BEKLE"], Decimal("0"))


class SmaKesisimSinyalleriTest(unittest.TestCase):

    def test_sinyal_listesi_fiyatla_ayni_uzunlukta(self):
        fiyatlar = [Decimal(n) for n in [1, 2, 3, 4, 5]]
        sinyaller = sma_kesisim_sinyalleri(fiyatlar, kisa=1, uzun=2)
        self.assertEqual(len(sinyaller), len(fiyatlar))

    def test_yukselen_seride_bir_alim(self):
        # Sürekli yükseliş -> kısa SMA uzun SMA üstünde -> bir kez AL
        fiyatlar = [Decimal(n) for n in [1, 2, 3, 4, 5]]
        sinyaller = sma_kesisim_sinyalleri(fiyatlar, kisa=1, uzun=2)
        self.assertEqual(sinyaller.count("AL"), 1)

    def test_kisa_uzundan_kucuk_olmali(self):
        with self.assertRaises(ValueError):
            sma_kesisim_sinyalleri([Decimal("1"), Decimal("2")], kisa=2, uzun=2)


if __name__ == "__main__":
    unittest.main()
