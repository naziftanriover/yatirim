"""EMA — Üssel Hareketli Ortalama (Exponential Moving Average).

Basit ortalamadan farkı: son günlere DAHA çok ağırlık verir, yani fiyat
değişimine daha hızlı tepki verir. MACD gibi göstergeler bunun üstüne kurulur.

Yöntem: ilk değer (seed) ilk 'periyot' fiyatın basit ortalaması;
sonraki her değer = k*bugünkü_fiyat + (1-k)*önceki_ema,  k = 2/(periyot+1).
"""

from decimal import Decimal


def ussel_hareketli_ortalama(fiyatlar: list, periyot: int) -> list:
    """Fiyat listesi için EMA serisini döndürür (periyot-1. indeksten itibaren)."""
    if periyot < 1:
        raise ValueError("periyot en az 1 olmalı.")
    if len(fiyatlar) < periyot:
        raise ValueError("Fiyat sayısı periyottan az olamaz.")

    k = Decimal(2) / (Decimal(periyot) + Decimal(1))
    bir_eksi_k = Decimal(1) - k

    # Seed: ilk 'periyot' fiyatın basit ortalaması.
    seed = sum(fiyatlar[:periyot], Decimal("0")) / Decimal(periyot)
    sonuc = [seed]

    for i in range(periyot, len(fiyatlar)):
        yeni = fiyatlar[i] * k + sonuc[-1] * bir_eksi_k
        sonuc.append(yeni)
    return sonuc
