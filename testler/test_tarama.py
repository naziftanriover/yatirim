"""Tarama & skorlama testleri (ÖNCE yazıldı)."""

import unittest
from decimal import Decimal

from yatirim.tarama.skor import hisse_skoru, en_iyiler, SkorSonucu


class HisseSkoruTest(unittest.TestCase):

    def test_mukemmel_aday_yuz_puan(self):
        # Ucuz + düşük borç + yukarı trend + aşırı alımda değil -> 100
        s = hisse_skoru(
            fk=Decimal("10"),
            borc_oz=Decimal("0.5"),
            yukari_trend=True,
            rsi=Decimal("50"),
        )
        self.assertIsInstance(s, SkorSonucu)
        self.assertEqual(s.skor, 100)
        self.assertEqual(len(s.gerekceler), 4)

    def test_en_kotu_aday_sifir_puan(self):
        s = hisse_skoru(
            fk=Decimal("30"),
            borc_oz=Decimal("2"),
            yukari_trend=False,
            rsi=Decimal("80"),
        )
        self.assertEqual(s.skor, 0)

    def test_karma_aday_elli_puan(self):
        # Ucuz (+25), yüksek borç (0), yukarı trend (+25), aşırı alım (0) -> 50
        s = hisse_skoru(
            fk=Decimal("10"),
            borc_oz=Decimal("2"),
            yukari_trend=True,
            rsi=Decimal("80"),
        )
        self.assertEqual(s.skor, 50)


class EnIyilerTest(unittest.TestCase):

    def test_skora_gore_sirali(self):
        sirali = en_iyiler({"A": 40, "B": 90, "C": 70})
        self.assertEqual(sirali, [("B", 90), ("C", 70), ("A", 40)])

    def test_bos_sozluk(self):
        self.assertEqual(en_iyiler({}), [])


if __name__ == "__main__":
    unittest.main()
