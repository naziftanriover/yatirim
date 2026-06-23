"""Öneri panosu: bir izleme listesini tarayıp en güçlü görünenleri sıralar.

Her sembol için fiyat + (varsa) temel veri çekilir, akıllı yorum motoru
çalıştırılır ve sinyal skoruna göre sıralanır. Ağ kısmı (tarama_yap) kullanıcının
makinesinde/Cloud'da çalışır; sıralama (sirala) saf ve test edilebilirdir.

DİKKAT: Bu bir öneri/özet panosudur, yatırım tavsiyesi DEĞİLDİR.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class TaramaSatiri:
    """Panodaki tek bir sembolün özeti."""

    sembol: str
    yon: str
    skor: int
    fiyat: Optional[Decimal] = None
    saglik_skoru: Optional[int] = None
    al_alt: Optional[Decimal] = None
    al_ust: Optional[Decimal] = None
    kar_al: Optional[Decimal] = None
    stop: Optional[Decimal] = None
    hata: Optional[str] = None


def sirala(satirlar: list) -> list:
    """Satırları sinyal skoruna göre BÜYÜKTEN küçüğe sıralar; hatalılar en sona."""
    return sorted(satirlar, key=lambda s: (s.hata is not None, -s.skor))


def tarama_yap(semboller: list) -> list:
    """Sembolleri tarar, her biri için TaramaSatiri üretir ve sıralı döndürür.

    İnternet ister (fiyat + temel veri). Bir sembol başarısız olursa o satır
    'hata' ile işaretlenir ve listenin sonuna konur; tarama durmaz.
    """
    from yatirim.veri.canli import fiyat_gecmisi, temel_veri
    from yatirim.temel.saglik import sirket_sagligi
    from yatirim.yorum.motor import hisse_yorumu

    satirlar = []
    for ham in semboller:
        sembol = ham.strip()
        if not sembol:
            continue
        try:
            fiyatlar = fiyat_gecmisi(sembol)
        except Exception:
            satirlar.append(TaramaSatiri(sembol=sembol, yon="—", skor=0, hata="veri yok"))
            continue

        # Temel veri opsiyonel: gelirse skora katılır, gelmezse atlanır.
        saglik_skoru = None
        try:
            saglik_skoru = sirket_sagligi(temel_veri(sembol)).skor
        except Exception:
            saglik_skoru = None

        try:
            y = hisse_yorumu(fiyatlar, saglik_skoru)
        except Exception:
            satirlar.append(TaramaSatiri(sembol=sembol, yon="—", skor=0, hata="yorum yok"))
            continue

        satirlar.append(TaramaSatiri(
            sembol=sembol,
            yon=y.yon,
            skor=y.skor,
            fiyat=fiyatlar[-1],
            saglik_skoru=saglik_skoru,
            al_alt=y.al_bolgesi[0],
            al_ust=y.al_bolgesi[1],
            kar_al=y.kar_al_hedefi,
            stop=y.stop_seviyesi,
        ))

    return sirala(satirlar)
