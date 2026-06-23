"""Basit hisse skorlama (0-100) ve sıralama.

Dört kritere bakar, her biri 25 puan:
  1. Ucuz mu?        F/K  < fk_esik           (varsayılan 15)
  2. Az mı borçlu?   Borç/Özkaynak < borc_esik (varsayılan 1)
  3. Yukarı trend mi? fiyat 'yukari_trend=True' (örn. fiyat > hareketli ortalama)
  4. Aşırı alımda değil mi? RSI < rsi_tavan    (varsayılan 70)

DİKKAT: Bu puan bir 'al' emri DEĞİLDİR. Sadece adayları aynı ölçütle
karşılaştırmana yarar. Eşikleri kendine göre değiştirebilirsin.
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class SkorSonucu:
    """Bir adayın skoru ve hangi kriterlerden puan aldığı."""

    skor: int                  # 0-100
    gerekceler: list = field(default_factory=list)  # puan veren kriterler


def hisse_skoru(
    fk: Decimal,
    borc_oz: Decimal,
    yukari_trend: bool,
    rsi: Decimal,
    *,
    fk_esik: Decimal = Decimal("15"),
    borc_esik: Decimal = Decimal("1"),
    rsi_tavan: Decimal = Decimal("70"),
) -> SkorSonucu:
    """Dört kritere göre 0-100 arası skor ve gerekçe listesi döndürür."""
    skor = 0
    gerekceler = []

    if fk < fk_esik:
        skor += 25
        gerekceler.append(f"Ucuz: F/K {fk} < {fk_esik}")
    if borc_oz < borc_esik:
        skor += 25
        gerekceler.append(f"Düşük borç: Borç/Özkaynak {borc_oz} < {borc_esik}")
    if yukari_trend:
        skor += 25
        gerekceler.append("Yukarı trend")
    if rsi < rsi_tavan:
        skor += 25
        gerekceler.append(f"Aşırı alımda değil: RSI {rsi} < {rsi_tavan}")

    return SkorSonucu(skor=skor, gerekceler=gerekceler)


def en_iyiler(skorlar: dict) -> list:
    """{isim: skor} sözlüğünü skora göre BÜYÜKTEN KÜÇÜĞE sıralar.

    Örn. {"A":40,"B":90,"C":70} -> [("B",90),("C",70),("A",40)]
    """
    return sorted(skorlar.items(), key=lambda ikili: ikili[1], reverse=True)
