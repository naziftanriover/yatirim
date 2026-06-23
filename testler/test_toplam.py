"""Toplam açık risk tavanı kuralının testleri (ÖNCE yazıldı).

Kural:
  - Aynı anda AÇIK tüm işlemlerin riski toplanır.
  - Bu toplam, ana paranın belirlenen yüzdesini (varsayılan %6) geçemez.
  - Her işlemin riski stop.py'deki 'riske_atilan' değeridir.

Çalıştırmak için proje kökünde:
    python3 -m unittest testler.test_toplam -v
"""

import unittest
from decimal import Decimal

from yatirim.risk.toplam import toplam_risk_kontrol, ToplamRiskSonucu


class ToplamRiskKontrolTest(unittest.TestCase):

    def test_acik_islem_yoksa_uygun(self):
        # Hiç açık işlem yok -> toplam risk 0 -> uygun.
        s = toplam_risk_kontrol(Decimal("100000"), [])
        self.assertIsInstance(s, ToplamRiskSonucu)
        self.assertTrue(s.uygun)
        self.assertEqual(s.toplam_risk, Decimal("0"))
        # Tavan = 100000 x %6 = 6000
        self.assertEqual(s.tavan_tutar, Decimal("6000"))

    def test_tavanin_altinda_uygun(self):
        # Riskler 2000 + 2000 = 4000 < 6000 tavan -> uygun.
        s = toplam_risk_kontrol(Decimal("100000"), [Decimal("2000"), Decimal("2000")])
        self.assertTrue(s.uygun)
        self.assertEqual(s.toplam_risk, Decimal("4000"))
        self.assertEqual(s.ihlaller, [])

    def test_tam_tavanda_uygun(self):
        # Toplam tam 6000 = tavan -> sınır dahil, uygun.
        s = toplam_risk_kontrol(Decimal("100000"), [Decimal("3000"), Decimal("3000")])
        self.assertTrue(s.uygun)
        self.assertEqual(s.toplam_risk, Decimal("6000"))

    def test_tavani_asarsa_uygun_degil(self):
        # 4000 + 3000 = 7000 > 6000 -> ihlal.
        s = toplam_risk_kontrol(Decimal("100000"), [Decimal("4000"), Decimal("3000")])
        self.assertFalse(s.uygun)
        self.assertEqual(s.toplam_risk, Decimal("7000"))
        self.assertEqual(len(s.ihlaller), 1)
        self.assertIn("toplam", s.ihlaller[0].lower())

    def test_negatif_risk_hata(self):
        with self.assertRaises(ValueError):
            toplam_risk_kontrol(Decimal("100000"), [Decimal("1000"), Decimal("-5")])

    def test_sermaye_sifir_veya_negatif_hata(self):
        with self.assertRaises(ValueError):
            toplam_risk_kontrol(Decimal("0"), [Decimal("100")])

    def test_kurus_hassasiyeti(self):
        # 1500.50 + 1499.50 = 3000.00 (Decimal ile tam)
        s = toplam_risk_kontrol(
            Decimal("100000"), [Decimal("1500.50"), Decimal("1499.50")]
        )
        self.assertEqual(s.toplam_risk, Decimal("3000.00"))
        self.assertTrue(s.uygun)


if __name__ == "__main__":
    unittest.main()
