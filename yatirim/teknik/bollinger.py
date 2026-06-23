"""Bollinger Bantları.

Orta bant = hareketli ortalama (SMA).
Üst/alt bant = orta ± k * standart sapma  (genelde k=2).

Bantlar fiyatın 'normal oynaklık aralığını' gösterir. Fiyat üst banda yapışırsa
görece pahalı/aşırı, alt banda yapışırsa görece ucuz/aşırı yorumlanabilir.
Standart sapma: pencere içindeki dalgalanmanın ölçüsü (popülasyon, n'e bölünür).
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BollingerSonucu:
    orta: list   # orta bant (SMA)
    ust: list    # üst bant
    alt: list    # alt bant


def bollinger_bantlari(
    fiyatlar: list,
    periyot: int = 20,
    k: Decimal = Decimal("2"),
) -> BollingerSonucu:
    """Her pencere için orta/üst/alt Bollinger bantlarını döndürür."""
    if periyot < 1:
        raise ValueError("periyot en az 1 olmalı.")
    if len(fiyatlar) < periyot:
        raise ValueError("Fiyat sayısı periyottan az olamaz.")

    orta, ust, alt = [], [], []
    for bas in range(len(fiyatlar) - periyot + 1):
        pencere = fiyatlar[bas:bas + periyot]
        ortalama = sum(pencere, Decimal("0")) / Decimal(periyot)

        # Popülasyon varyansı = ortalamadan sapmaların karelerinin ortalaması.
        varyans = sum(((x - ortalama) ** 2 for x in pencere), Decimal("0")) / Decimal(periyot)
        std = varyans.sqrt()

        orta.append(ortalama)
        ust.append(ortalama + k * std)
        alt.append(ortalama - k * std)

    return BollingerSonucu(orta=orta, ust=ust, alt=alt)
