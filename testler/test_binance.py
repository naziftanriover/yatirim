"""Binance salt-okunur adaptörü — imzalama testleri (internet GEREKTİRMEZ).

İmza, Binance'in resmî dokümanındaki test vektörüyle doğrulanır. Ağ çağrısı
(bakiye_getir) burada test edilmez; kendi makinende/Cloud'da çalışır.
"""

import unittest

from yatirim.borsa.binance_oku import imzala, imzali_sorgu


class ImzalaTest(unittest.TestCase):

    # Binance API dokümanındaki resmî örnek.
    SECRET = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
    SORGU = ("symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1"
             "&price=0.1&recvWindow=5000&timestamp=1499827319559")
    BEKLENEN = "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"

    def test_resmi_test_vektoru(self):
        self.assertEqual(imzala(self.SORGU, self.SECRET), self.BEKLENEN)

    def test_imzali_sorgu_imza_ekler(self):
        sonuc = imzali_sorgu({"a": "1", "b": "2"}, "gizli")
        self.assertTrue(sonuc.startswith("a=1&b=2&signature="))


if __name__ == "__main__":
    unittest.main()
