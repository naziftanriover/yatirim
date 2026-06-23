"""Emir Özeti testleri (ÖNCE yazıldı). Emir GÖNDERMEZ; sadece hazırlar."""

import unittest
from decimal import Decimal

from yatirim.emir.ozet import emir_ozeti, EmirOzeti
from yatirim.borsa.binance_oku import binance_islem_linki


class EmirOzetiTest(unittest.TestCase):

    def test_risk_bazli_adet(self):
        # sermaye 100000, %2 risk = 2000; giriş 100, stop 95 -> birim risk 5
        # önerilen adet = 2000 / 5 = 400
        o = emir_ozeti("Olumlu", Decimal("100000"), Decimal("100"),
                       Decimal("95"), Decimal("120"))
        self.assertIsInstance(o, EmirOzeti)
        self.assertEqual(o.onerilen_adet, 400)
        self.assertEqual(o.riske_atilan, Decimal("2000"))
        self.assertEqual(o.risk_yuzde, Decimal("2.00"))
        self.assertIn("AL", o.taraf)

    def test_notr_izle(self):
        o = emir_ozeti("Nötr", Decimal("100000"), Decimal("100"),
                       Decimal("95"), Decimal("120"))
        self.assertIn("İZLE", o.taraf.upper())

    def test_stop_giristen_buyukse_hata(self):
        with self.assertRaises(ValueError):
            emir_ozeti("Olumlu", Decimal("100000"), Decimal("100"),
                       Decimal("105"), Decimal("120"))


class BinanceLinkTest(unittest.TestCase):

    def test_kripto_linki(self):
        link = binance_islem_linki("BTC-USD")
        self.assertIsNotNone(link)
        self.assertIn("BTC_USDT", link)

    def test_hisse_link_yok(self):
        self.assertIsNone(binance_islem_linki("AAPL"))


if __name__ == "__main__":
    unittest.main()
