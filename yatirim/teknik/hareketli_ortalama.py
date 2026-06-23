"""Basit Hareketli Ortalama (SMA - Simple Moving Average).

Hareketli ortalama: son N günün fiyat ortalaması. Fiyattaki günlük gürültüyü
yumuşatıp 'genel yön'ü (trend) görmeye yarar. Örn. 'fiyat 50 günlük ortalamanın
üstünde' yaygın bir yukarı-trend işaretidir.
"""

from decimal import Decimal


def basit_hareketli_ortalama(fiyatlar: list, periyot: int) -> list:
    """Verilen fiyat listesi için her pencerenin ortalamasını döndürür.

    Örn. fiyatlar=[10,20,30,40], periyot=2 -> [15, 25, 35]
    (her ardışık 2 fiyatın ortalaması).

    Hata: periyot < 1 ise ya da fiyat sayısı periyottan azsa ValueError.
    """
    if periyot < 1:
        raise ValueError("periyot en az 1 olmalı.")
    if len(fiyatlar) < periyot:
        raise ValueError("Fiyat sayısı periyottan az olamaz.")

    sonuc = []
    # Pencereyi listede kaydırarak her adımda ortalama al.
    for bas in range(len(fiyatlar) - periyot + 1):
        pencere = fiyatlar[bas:bas + periyot]
        sonuc.append(sum(pencere, Decimal("0")) / Decimal(periyot))
    return sonuc
