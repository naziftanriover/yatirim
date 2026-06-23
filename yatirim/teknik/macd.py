"""MACD — Moving Average Convergence Divergence.

Üç parça:
  - macd_cizgi = kısa EMA (12) - uzun EMA (26)   -> momentumun yönü
  - sinyal     = macd_cizgi'nin EMA'sı (9)        -> tetik çizgisi
  - histogram  = macd_cizgi - sinyal              -> ivmenin gücü

Yorum (genel): macd_cizgi sinyali yukarı keserse 'al' eğilimi, aşağı keserse
'sat' eğilimi olarak okunur. Tek başına karar verdirmez.
"""

from dataclasses import dataclass
from decimal import Decimal

from yatirim.teknik.ema import ussel_hareketli_ortalama


@dataclass(frozen=True)
class MacdSonucu:
    macd_cizgi: list
    sinyal: list
    histogram: list


def macd(
    fiyatlar: list,
    kisa: int = 12,
    uzun: int = 26,
    sinyal_periyot: int = 9,
) -> MacdSonucu:
    """Fiyat serisi için MACD çizgisi, sinyal ve histogramı hesaplar."""
    if kisa >= uzun:
        raise ValueError("kisa periyot, uzun periyottan küçük olmalı.")
    # Sinyal için en az 'sinyal_periyot' adet macd değeri lazım.
    gereken = uzun + sinyal_periyot - 1
    if len(fiyatlar) < gereken:
        raise ValueError(f"MACD için en az {gereken} fiyat gerekir.")

    ema_kisa = ussel_hareketli_ortalama(fiyatlar, kisa)
    ema_uzun = ussel_hareketli_ortalama(fiyatlar, uzun)

    # İki EMA farklı uzunlukta; uzun EMA'nın başladığı yerden hizala.
    n_u = len(ema_uzun)
    ema_kisa_hizali = ema_kisa[-n_u:]
    macd_cizgi = [a - b for a, b in zip(ema_kisa_hizali, ema_uzun)]

    sinyal = ussel_hareketli_ortalama(macd_cizgi, sinyal_periyot)
    n_s = len(sinyal)
    macd_hizali = macd_cizgi[-n_s:]
    histogram = [a - b for a, b in zip(macd_hizali, sinyal)]

    return MacdSonucu(macd_cizgi=macd_cizgi, sinyal=sinyal, histogram=histogram)
