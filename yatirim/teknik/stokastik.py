"""Stokastik Osilatör (%K).

Kapanışın, son 'periyot' içindeki en düşük-en yüksek aralığında NEREDE durduğunu
0-100 arası gösterir.
  %K = (kapanış - en_düşük) / (en_yüksek - en_düşük) * 100
80 üstü 'aşırı alım', 20 altı 'aşırı satım' bölgesi yorumlanır.

Not: Bu basit sürüm yalnız kapanış fiyatlarını kullanır (gerçek piyasada
en yüksek/en düşük günlük değerler de kullanılabilir).
"""

from decimal import Decimal

_IKI_ONDALIK = Decimal("0.01")


def stokastik_k(fiyatlar: list, periyot: int = 14) -> list:
    """Her pencere için Stokastik %K değerini (2 ondalık) döndürür."""
    if periyot < 1:
        raise ValueError("periyot en az 1 olmalı.")
    if len(fiyatlar) < periyot:
        raise ValueError("Fiyat sayısı periyottan az olamaz.")

    sonuc = []
    for bas in range(len(fiyatlar) - periyot + 1):
        pencere = fiyatlar[bas:bas + periyot]
        en_dusuk = min(pencere)
        en_yuksek = max(pencere)
        kapanis = pencere[-1]

        aralik = en_yuksek - en_dusuk
        if aralik == 0:
            # Tüm fiyatlar eşitse aralık yok; tarafsız 50 verelim.
            sonuc.append(Decimal("50.00"))
        else:
            k = (kapanis - en_dusuk) / aralik * Decimal("100")
            sonuc.append(k.quantize(_IKI_ONDALIK))
    return sonuc
