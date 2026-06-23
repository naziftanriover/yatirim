"""Öneri / pazar panosu: sembolleri tarayıp fiyat, günlük değişim ve sinyal verir.

Her sembol için fiyat (+ istenirse temel veri) çekilir, akıllı yorum motoru
çalıştırılır ve sinyal skoruna göre sıralanır. Ağ kısmı (tarama_yap) internet
ister; sıralama (sirala) ve günlük değişim (gunluk_degisim_yuzde) saf ve test edilebilir.

DİKKAT: Bu bir öneri/özet panosudur, yatırım tavsiyesi DEĞİLDİR.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

_IKI_ONDALIK = Decimal("0.01")


@dataclass(frozen=True)
class TaramaSatiri:
    """Panodaki tek bir sembolün özeti."""

    sembol: str
    yon: str
    skor: int
    fiyat: Optional[Decimal] = None
    gunluk_degisim: Optional[Decimal] = None   # son güne göre % değişim
    saglik_skoru: Optional[int] = None
    al_alt: Optional[Decimal] = None
    al_ust: Optional[Decimal] = None
    kar_al: Optional[Decimal] = None
    stop: Optional[Decimal] = None
    hata: Optional[str] = None


def gunluk_degisim_yuzde(fiyatlar: list) -> Optional[Decimal]:
    """Son iki kapanışa göre yüzde değişim (2 ondalık). Yetersiz veride None."""
    if len(fiyatlar) < 2:
        return None
    onceki = fiyatlar[-2]
    son = fiyatlar[-1]
    if onceki == 0:
        return None
    return ((son - onceki) / onceki * Decimal("100")).quantize(_IKI_ONDALIK)


def sirala(satirlar: list) -> list:
    """Satırları sinyal skoruna göre BÜYÜKTEN küçüğe sıralar; hatalılar en sona."""
    return sorted(satirlar, key=lambda s: (s.hata is not None, -s.skor))


def tarama_yap(semboller: list, temel_dahil: bool = True, periyot: str = "6mo") -> list:
    """Sembolleri tarar, her biri için TaramaSatiri üretir ve sıralı döndürür.

    temel_dahil=False: temel veriyi atlar (çok sembollü panellerde HIZLI olur).
    periyot: fiyat geçmişi süresi (paneller için '3mo' yeterli ve hızlı).
    Bir sembol başarısız olursa o satır 'hata' ile işaretlenir; tarama durmaz.
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
            fiyatlar = fiyat_gecmisi(sembol, periyot)
        except Exception:
            satirlar.append(TaramaSatiri(sembol=sembol, yon="—", skor=0, hata="veri yok"))
            continue

        degisim = gunluk_degisim_yuzde(fiyatlar)

        saglik_skoru = None
        if temel_dahil:
            try:
                saglik_skoru = sirket_sagligi(temel_veri(sembol)).skor
            except Exception:
                saglik_skoru = None

        try:
            y = hisse_yorumu(fiyatlar, saglik_skoru)
        except Exception:
            satirlar.append(TaramaSatiri(
                sembol=sembol, yon="—", skor=0, fiyat=fiyatlar[-1],
                gunluk_degisim=degisim, hata="yorum yok"))
            continue

        satirlar.append(TaramaSatiri(
            sembol=sembol,
            yon=y.yon,
            skor=y.skor,
            fiyat=fiyatlar[-1],
            gunluk_degisim=degisim,
            saglik_skoru=saglik_skoru,
            al_alt=y.al_bolgesi[0],
            al_ust=y.al_bolgesi[1],
            kar_al=y.kar_al_hedefi,
            stop=y.stop_seviyesi,
        ))

    return sirala(satirlar)
