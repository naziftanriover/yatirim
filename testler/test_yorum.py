"""Akıllı yorum motoru testleri (ÖNCE yazıldı).

Motor; teknik + temel metrikleri birleştirip yön, al bölgesi, kâr-al hedefi,
stop seviyesi ve gerekçeler üretir. Tavsiye değil; gerekçeli, hesaplanmış yorum.
"""

import unittest
from decimal import Decimal

from yatirim.yorum.motor import yorumla, MetrikSeti, Yorum


def D(x):
    return Decimal(str(x))


class YorumlaTest(unittest.TestCase):

    def _metrik(self, **kw):
        varsayilan = dict(
            fiyat=D("110"), sma=D("105"), rsi=D("50"),
            macd_hist=D("0.5"), stokastik=D("50"),
            destek=D("100"), direnc=D("120"), saglik_skoru=60,
        )
        varsayilan.update(kw)
        return MetrikSeti(**varsayilan)

    def test_guclu_olumlu(self):
        # Trend yukarı (+1), RSI 25 oversold (+1), MACD+ (+1), stoch 15 (+1), sağlık 80 (+1) = 5
        y = yorumla(self._metrik(rsi=D("25"), stokastik=D("15"), saglik_skoru=80))
        self.assertIsInstance(y, Yorum)
        self.assertEqual(y.skor, 5)
        self.assertEqual(y.yon, "Olumlu")
        self.assertTrue(len(y.gerekceler) >= 1)

    def test_guclu_zayif(self):
        # Trend aşağı (-1), RSI 80 (-1), MACD- (-1), stoch 90 (-1), sağlık 30 (-1) = -5
        y = yorumla(self._metrik(
            fiyat=D("95"), sma=D("105"), rsi=D("80"),
            macd_hist=D("-0.5"), stokastik=D("90"), saglik_skoru=30,
        ))
        self.assertEqual(y.skor, -5)
        self.assertEqual(y.yon, "Zayıf")

    def test_notr(self):
        # Trend yukarı (+1), MACD- (-1), gerisi nötr = 0
        y = yorumla(self._metrik(
            rsi=D("50"), macd_hist=D("-0.1"), stokastik=D("50"), saglik_skoru=60,
        ))
        self.assertEqual(y.yon, "Nötr")

    def test_seviyeler_hesaplaniyor(self):
        # destek 100, direnç 120, stop %3 -> stop 97, al bölgesi alt 100, kâr-al 120
        y = yorumla(self._metrik(), stop_yuzde=D("0.03"))
        self.assertEqual(y.al_bolgesi[0], D("100"))
        self.assertEqual(y.kar_al_hedefi, D("120"))
        self.assertEqual(y.stop_seviyesi, D("97.00"))

    def test_eksik_veri_coker_degil(self):
        # Bazı metrikler None -> motor yine çalışır (o sinyali 0 sayar)
        y = yorumla(MetrikSeti(
            fiyat=D("110"), sma=None, rsi=None, macd_hist=None,
            stokastik=None, destek=D("100"), direnc=D("120"), saglik_skoru=None,
        ))
        self.assertIn(y.yon, ("Olumlu", "Zayıf", "Nötr"))
        self.assertTrue(y.uyari)  # risk uyarısı her zaman var


if __name__ == "__main__":
    unittest.main()
