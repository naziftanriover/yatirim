"""Uyarı koşulları.

Belirlediğin bir koşul (fiyat hedefi, RSI eşiği) oluşunca 'tetiklendi' diyen
saf fonksiyonlar. Karar/işlem yok; sadece haber verir.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class UyariSonucu:
    """Bir uyarı koşulunun sonucu."""

    tetiklendi: bool   # Koşul oluştu mu?
    mesaj: str         # İnsan-okur açıklama.


def fiyat_uyarisi(guncel_fiyat: Decimal, hedef: Decimal, yon: str) -> UyariSonucu:
    """Fiyat bir hedefe ulaşınca uyarır.

    yon='ust' -> fiyat hedefe ULAŞIR/GEÇERSE tetiklenir (örn. kâr-al seviyesi).
    yon='alt' -> fiyat hedefin ALTINA inerse tetiklenir (örn. izleme seviyesi).
    """
    if yon == "ust":
        tetik = guncel_fiyat >= hedef
        mesaj = (
            f"Fiyat {guncel_fiyat}, üst hedef {hedef}'e ulaştı."
            if tetik else
            f"Fiyat {guncel_fiyat}, üst hedef {hedef}'in altında."
        )
    elif yon == "alt":
        tetik = guncel_fiyat <= hedef
        mesaj = (
            f"Fiyat {guncel_fiyat}, alt hedef {hedef}'in altına indi."
            if tetik else
            f"Fiyat {guncel_fiyat}, alt hedef {hedef}'in üstünde."
        )
    else:
        raise ValueError("yon yalnızca 'ust' veya 'alt' olabilir.")

    return UyariSonucu(tetiklendi=tetik, mesaj=mesaj)


def rsi_uyarisi(
    rsi_degeri: Decimal,
    asiri_alim: Decimal = Decimal("70"),
    asiri_satim: Decimal = Decimal("30"),
) -> UyariSonucu:
    """RSI aşırı alım/satım bölgesine girince uyarır.

    rsi >= asiri_alim  -> 'aşırı alım' (çok yükselmiş olabilir)
    rsi <= asiri_satim -> 'aşırı satım' (çok düşmüş olabilir)
    Arası -> uyarı yok.
    """
    if rsi_degeri >= asiri_alim:
        return UyariSonucu(True, f"RSI {rsi_degeri}: aşırı alım bölgesi (>= {asiri_alim}).")
    if rsi_degeri <= asiri_satim:
        return UyariSonucu(True, f"RSI {rsi_degeri}: aşırı satım bölgesi (<= {asiri_satim}).")
    return UyariSonucu(False, f"RSI {rsi_degeri}: normal bölge.")
