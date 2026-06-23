"""Backtest icra motoru + SMA kesişim strateji sinyalleri.

İki parça:
  1) backtest(...)              -> verilen AL/SAT/BEKLE sinyallerini sahte parayla uygular.
  2) sma_kesisim_sinyalleri(...) -> kısa ve uzun hareketli ortalamanın kesişiminden
                                    AL/SAT sinyali üretir.
Mimari neden ayrık? Strateji (sinyal üretimi) ile icra (parayı yönetme) ayrı dursun ki
her birini tek başına test edebilelim ve farklı stratejiler deneyebilelim.
"""

from dataclasses import dataclass
from decimal import Decimal

_GECERLI_SINYALLER = {"AL", "SAT", "BEKLE"}
_IKI_ONDALIK = Decimal("0.01")


@dataclass(frozen=True)
class BacktestSonucu:
    """Backtest çıktısı (sahte para sonucu)."""

    son_deger: Decimal       # simülasyon sonunda toplam değer (nakit + pozisyon)
    getiri_yuzde: Decimal    # başlangıca göre yüzde getiri
    islem_sayisi: int        # kaç alım/satım yapıldı


def backtest(fiyatlar: list, sinyaller: list, baslangic_nakit: Decimal) -> BacktestSonucu:
    """AL/SAT/BEKLE sinyallerini fiyat serisinde sahte parayla uygular.

    Kurallar (basit model):
      - "AL"  : elde nakit varsa, o günün fiyatından TÜM nakitle alım yapılır.
      - "SAT" : elde pozisyon varsa, o günün fiyatından tamamı satılır.
      - "BEKLE": işlem yok.
    Sonda hâlâ pozisyon varsa son fiyatla değerlenir.

    Hata: liste uzunlukları farklıysa, başlangıç nakdi pozitif değilse,
    ya da geçersiz bir sinyal varsa ValueError.
    """
    if len(fiyatlar) != len(sinyaller):
        raise ValueError("fiyatlar ve sinyaller aynı uzunlukta olmalı.")
    if baslangic_nakit <= 0:
        raise ValueError("baslangic_nakit pozitif olmalı.")
    if len(fiyatlar) == 0:
        raise ValueError("fiyat listesi boş olamaz.")

    nakit = baslangic_nakit
    adet = Decimal("0")
    islem_sayisi = 0

    for fiyat, sinyal in zip(fiyatlar, sinyaller):
        if sinyal not in _GECERLI_SINYALLER:
            raise ValueError(f"Geçersiz sinyal: {sinyal} (AL/SAT/BEKLE olmalı).")
        if sinyal == "AL" and nakit > 0:
            adet += nakit / fiyat
            nakit = Decimal("0")
            islem_sayisi += 1
        elif sinyal == "SAT" and adet > 0:
            nakit += adet * fiyat
            adet = Decimal("0")
            islem_sayisi += 1
        # "BEKLE" ya da koşulu tutmayan durumda hiçbir şey yapma.

    son_fiyat = fiyatlar[-1]
    son_deger = nakit + adet * son_fiyat
    getiri = (son_deger - baslangic_nakit) / baslangic_nakit * Decimal("100")

    return BacktestSonucu(
        son_deger=son_deger,
        getiri_yuzde=getiri.quantize(_IKI_ONDALIK),
        islem_sayisi=islem_sayisi,
    )


def _sma_son(fiyatlar: list, i: int, periyot: int):
    """i. indekste biten 'periyot' uzunluklu basit ortalama. Yetersizse None."""
    if i < periyot - 1:
        return None
    pencere = fiyatlar[i - periyot + 1:i + 1]
    return sum(pencere, Decimal("0")) / Decimal(periyot)


def sma_kesisim_sinyalleri(fiyatlar: list, kisa: int, uzun: int) -> list:
    """Kısa SMA, uzun SMA'yı yukarı keserse 'AL'; aşağı keserse 'SAT' üretir.

    Mantık: kısa ortalama uzun ortalamanın Üstüne çıkınca yükseliş başlangıcı (AL),
    altına inince düşüş başlangıcı (SAT) varsayılır. Diğer günler 'BEKLE'.

    Hata: kisa < 1 ya da kisa >= uzun ise ValueError.
    """
    if kisa < 1:
        raise ValueError("kisa periyot en az 1 olmalı.")
    if kisa >= uzun:
        raise ValueError("kisa periyot, uzun periyottan küçük olmalı.")

    n = len(fiyatlar)
    sinyaller = ["BEKLE"] * n
    onceki_iliski = None  # 1: kısa üstte, -1: kısa altta, 0: eşit

    for i in range(n):
        ks = _sma_son(fiyatlar, i, kisa)
        us = _sma_son(fiyatlar, i, uzun)
        if ks is None or us is None:
            continue  # iki ortalama da hazır değil -> BEKLE

        iliski = 1 if ks > us else (-1 if ks < us else 0)

        if onceki_iliski is None:
            # İlk karşılaştırma noktası: mevcut duruma göre giriş sinyali.
            if iliski > 0:
                sinyaller[i] = "AL"
            elif iliski < 0:
                sinyaller[i] = "SAT"
        else:
            # Kesişim = ilişkinin yön değiştirmesi.
            if onceki_iliski <= 0 and iliski > 0:
                sinyaller[i] = "AL"
            elif onceki_iliski >= 0 and iliski < 0:
                sinyaller[i] = "SAT"

        onceki_iliski = iliski

    return sinyaller
