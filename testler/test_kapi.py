"""Risk kapısı testleri (ÖNCE yazıldı).

islem_degerlendir: bir işlem teklifini dört risk kuralından geçirir ve
tek bir karar (uygun mu + nedenler) döndürür.
"""

import unittest
from decimal import Decimal

from yatirim.risk.kapi import islem_degerlendir, IslemTeklifi, IslemKarari


def teklif(**kw):
    """Testlerde kısa yazım için varsayılan geçerli bir teklif üretir."""
    varsayilan = dict(
        toplam_sermaye=Decimal("100000"),
        giris_fiyati=Decimal("100"),
        stop_fiyati=Decimal("98"),
        adet=Decimal("100"),
        yon="uzun",
        teminat=Decimal("10000"),
        kaldirac_orani=Decimal("1"),
        mevcut_riskler=[],
    )
    varsayilan.update(kw)
    return IslemTeklifi(**varsayilan)


class IslemDegerlendirTest(unittest.TestCase):

    def test_tamamen_uygun_islem(self):
        # risk = (100-98)*100 = 200; 2% tavan = 2000; toplam 200 < 6000 -> uygun
        k = islem_degerlendir(teklif())
        self.assertIsInstance(k, IslemKarari)
        self.assertTrue(k.uygun)
        self.assertEqual(k.riske_atilan, Decimal("200"))
        self.assertEqual(k.ihlaller, [])

    def test_stop_yoksa_uygun_degil(self):
        k = islem_degerlendir(teklif(stop_fiyati=None))
        self.assertFalse(k.uygun)
        self.assertTrue(any("stop" in i.lower() for i in k.ihlaller))

    def test_tek_islem_riski_yuzde_ikiyi_asarsa_uygun_degil(self):
        # giris 100, stop 50, adet 100 -> risk 5000 > 2000 (%2) -> ihlal
        k = islem_degerlendir(teklif(stop_fiyati=Decimal("50")))
        self.assertFalse(k.uygun)
        self.assertTrue(any("tek işlem" in i.lower() for i in k.ihlaller))

    def test_teminat_yuzde_yirmiyi_asarsa_uygun_degil(self):
        k = islem_degerlendir(teklif(teminat=Decimal("25000")))
        self.assertFalse(k.uygun)
        self.assertTrue(any("teminat" in i.lower() for i in k.ihlaller))

    def test_kaldirac_bes_kati_asarsa_uygun_degil(self):
        k = islem_degerlendir(teklif(kaldirac_orani=Decimal("6")))
        self.assertFalse(k.uygun)
        self.assertTrue(any("kaldıraç" in i.lower() for i in k.ihlaller))

    def test_toplam_risk_tavani_asarsa_uygun_degil(self):
        # bu işlem riski 200; mevcut 5900 -> toplam 6100 > 6000 -> ihlal
        k = islem_degerlendir(teklif(mevcut_riskler=[Decimal("5900")]))
        self.assertFalse(k.uygun)
        self.assertTrue(any("toplam" in i.lower() for i in k.ihlaller))

    def test_birden_fazla_ihlal_birlesir(self):
        # teminat %25 + kaldıraç 6x -> en az 2 ihlal
        k = islem_degerlendir(teklif(teminat=Decimal("25000"), kaldirac_orani=Decimal("6")))
        self.assertFalse(k.uygun)
        self.assertGreaterEqual(len(k.ihlaller), 2)


if __name__ == "__main__":
    unittest.main()
