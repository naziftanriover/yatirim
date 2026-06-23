"""CSV fiyat okuyucu testleri (ÖNCE yazıldı).

Geçici (tempfile) CSV dosyaları yazıp okuyarak test ederiz; gerçek dosya gerekmez.
"""

import os
import tempfile
import unittest
from decimal import Decimal

from yatirim.veri.csv_okuyucu import fiyatlari_oku


def gecici_csv(icerik: str) -> str:
    """İçeriği geçici bir .csv dosyasına yazar, yolunu döndürür."""
    fd, yol = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(icerik)
    return yol


class CsvOkuyucuTest(unittest.TestCase):

    def test_kapanis_sutununu_okur(self):
        yol = gecici_csv("tarih,kapanis\n2024-01-01,10.5\n2024-01-02,11.0\n")
        try:
            fiyatlar = fiyatlari_oku(yol)
            self.assertEqual(fiyatlar, [Decimal("10.5"), Decimal("11.0")])
        finally:
            os.remove(yol)

    def test_ozel_sutun_adi(self):
        yol = gecici_csv("date,close\n2024-01-01,3.25\n")
        try:
            fiyatlar = fiyatlari_oku(yol, sutun="close")
            self.assertEqual(fiyatlar, [Decimal("3.25")])
        finally:
            os.remove(yol)

    def test_olmayan_sutun_hata(self):
        yol = gecici_csv("tarih,kapanis\n2024-01-01,10.5\n")
        try:
            with self.assertRaises(ValueError):
                fiyatlari_oku(yol, sutun="acilis")
        finally:
            os.remove(yol)

    def test_bozuk_sayi_hata(self):
        yol = gecici_csv("tarih,kapanis\n2024-01-01,abc\n")
        try:
            with self.assertRaises(ValueError):
                fiyatlari_oku(yol)
        finally:
            os.remove(yol)

    def test_olmayan_dosya_hata(self):
        with self.assertRaises(FileNotFoundError):
            fiyatlari_oku("/asla/olmayan/dosya.csv")


if __name__ == "__main__":
    unittest.main()
