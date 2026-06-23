"""Şirket sağlığı değerlendirici testleri (ÖNCE yazıldı)."""

import unittest
from decimal import Decimal

from yatirim.temel.saglik import sirket_sagligi, TemelVeri, SirketSagligi


def D(x):
    return Decimal(str(x))


class SirketSagligiTest(unittest.TestCase):

    def test_tamamen_saglikli(self):
        veri = TemelVeri(
            fk=D("12"), borc_ozkaynak=D("0.5"), cari_oran=D("2.0"),
            roe=D("0.20"), net_marj=D("0.15"),
            gelir_buyume=D("0.10"), kar_buyume=D("0.08"),
        )
        s = sirket_sagligi(veri)
        self.assertIsInstance(s, SirketSagligi)
        self.assertEqual(s.skor, 100)
        self.assertEqual(s.durum, "Sağlıklı")
        self.assertEqual(s.zayif, [])
        self.assertEqual(s.degerlendirilen, 7)

    def test_tamamen_riskli(self):
        veri = TemelVeri(
            fk=D("-5"), borc_ozkaynak=D("3"), cari_oran=D("0.8"),
            roe=D("0.02"), net_marj=D("-0.10"),
            gelir_buyume=D("-0.05"), kar_buyume=D("-0.10"),
        )
        s = sirket_sagligi(veri)
        self.assertEqual(s.skor, 0)
        self.assertEqual(s.durum, "Riskli")
        self.assertEqual(s.guclu, [])

    def test_karma_ve_eksik_veri(self):
        # Sadece 2 alan var: fk iyi, borç kötü -> 1/2 = %50 -> İzlenmeli
        veri = TemelVeri(fk=D("10"), borc_ozkaynak=D("2"))
        s = sirket_sagligi(veri)
        self.assertEqual(s.degerlendirilen, 2)
        self.assertEqual(s.skor, 50)
        self.assertEqual(s.durum, "İzlenmeli")

    def test_hic_veri_yoksa_yetersiz(self):
        s = sirket_sagligi(TemelVeri())
        self.assertEqual(s.degerlendirilen, 0)
        self.assertEqual(s.durum, "Veri yetersiz")


if __name__ == "__main__":
    unittest.main()
