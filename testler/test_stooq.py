"""Stooq yedek kaynağının internet GEREKTİRMEYEN parçalarının testleri."""

import unittest
from decimal import Decimal

from yatirim.veri.canli import _stooq_kod, _stooq_csv_parse


class StooqKodTest(unittest.TestCase):

    def test_abd_hissesi_us_eki(self):
        self.assertEqual(_stooq_kod("AAPL"), "aapl.us")

    def test_bist_tr_eki(self):
        self.assertEqual(_stooq_kod("THYAO.IS"), "thyao.tr")

    def test_kripto_desteklenmez(self):
        self.assertIsNone(_stooq_kod("BTC-USD"))

    def test_vadeli_desteklenmez(self):
        self.assertIsNone(_stooq_kod("GC=F"))


class StooqCsvParseTest(unittest.TestCase):

    ORNEK = (
        "Date,Open,High,Low,Close,Volume\n"
        "2024-01-01,10,11,9,10.5,1000\n"
        "2024-01-02,10.5,12,10,11.0,2000\n"
    )

    def test_close_sutununu_okur(self):
        sonuc = _stooq_csv_parse(self.ORNEK)
        self.assertEqual(sonuc, [Decimal("10.5"), Decimal("11.0")])

    def test_son_n_kirpar(self):
        sonuc = _stooq_csv_parse(self.ORNEK, son_n=1)
        self.assertEqual(sonuc, [Decimal("11.0")])

    def test_bozuk_baslik_bos_doner(self):
        self.assertEqual(_stooq_csv_parse("alakasiz,veri\n1,2"), [])

    def test_bos_metin_bos_doner(self):
        self.assertEqual(_stooq_csv_parse(""), [])


if __name__ == "__main__":
    unittest.main()
