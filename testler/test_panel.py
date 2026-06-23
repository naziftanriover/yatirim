"""Tarama panosu sıralama testleri (ÖNCE yazıldı).

Ağ (tarama_yap) burada test edilmez; saf sıralama (sirala) test edilir.
"""

import unittest

from yatirim.tarama.panel import sirala, TaramaSatiri


class SiralaTest(unittest.TestCase):

    def test_skora_gore_azalan(self):
        satirlar = [
            TaramaSatiri(sembol="A", yon="Nötr", skor=1),
            TaramaSatiri(sembol="B", yon="Olumlu", skor=5),
            TaramaSatiri(sembol="C", yon="Zayıf", skor=-3),
        ]
        sirali = sirala(satirlar)
        self.assertEqual([s.sembol for s in sirali], ["B", "A", "C"])

    def test_hatalilar_sona_gider(self):
        satirlar = [
            TaramaSatiri(sembol="X", yon="-", skor=0, hata="veri yok"),
            TaramaSatiri(sembol="Y", yon="Olumlu", skor=4),
        ]
        sirali = sirala(satirlar)
        self.assertEqual([s.sembol for s in sirali], ["Y", "X"])

    def test_bos_liste(self):
        self.assertEqual(sirala([]), [])


if __name__ == "__main__":
    unittest.main()
