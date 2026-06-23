"""Akıllı yorum motoru.

Teknik göstergeleri (trend, RSI, MACD, Stokastik) ve temel sağlık skorunu
birleştirip bir 'yön' ve HESAPLANMIŞ seviyeler üretir:
  - al bölgesi   : destek civarı (ucuza yakın alım için izlenebilir aralık)
  - kâr-al hedefi: direnç civarı
  - stop seviyesi: desteğin biraz altı (zararı sınırlamak için)

DİKKAT: Yatırım tavsiyesi DEĞİLDİR. Gerekçeli bir özettir, yanılabilir.
Seviyeler uydurulmaz; destek/direnç ve stop oranından hesaplanır.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

_IKI_ONDALIK = Decimal("0.01")
_UYARI = (
    "Bu bir yatırım tavsiyesi değildir; göstergelere dayalı, hesaplanmış bir "
    "özettir ve yanılabilir. İşleme girmeden önce mutlaka stop (zarar-kes) koy "
    "ve risk kurallarını uygula. Kararı sen verirsin."
)


@dataclass(frozen=True)
class MetrikSeti:
    """Yorum için gereken metrikler (eksik olanlar None bırakılabilir)."""

    fiyat: Decimal               # güncel (son) fiyat
    destek: Decimal              # yakın destek (örn. son 20 günün en düşüğü)
    direnc: Decimal              # yakın direnç (örn. son 20 günün en yükseği)
    sma: Optional[Decimal] = None
    rsi: Optional[Decimal] = None
    macd_hist: Optional[Decimal] = None
    stokastik: Optional[Decimal] = None
    saglik_skoru: Optional[int] = None


@dataclass(frozen=True)
class Yorum:
    """Motorun ürettiği gerekçeli yorum (sadece bilgi)."""

    yon: str                 # "Olumlu" / "Zayıf" / "Nötr"
    skor: int                # -5..+5 (sinyallerin toplamı)
    al_bolgesi: tuple        # (alt, üst) Decimal
    kar_al_hedefi: Decimal
    stop_seviyesi: Decimal
    gerekceler: list = field(default_factory=list)
    uyari: str = _UYARI


def yorumla(m: MetrikSeti, *, stop_yuzde: Decimal = Decimal("0.03")) -> Yorum:
    """Metrikleri birleştirip yön + seviyeler + gerekçeler döndürür."""
    skor = 0
    gerekceler = []

    # 1) Trend: fiyat hareketli ortalamanın üstünde mi?
    if m.sma is not None:
        if m.fiyat > m.sma:
            skor += 1
            gerekceler.append("Fiyat ortalamanın ÜSTÜNDE (yukarı trend).")
        else:
            skor -= 1
            gerekceler.append("Fiyat ortalamanın ALTINDA (zayıf trend).")

    # 2) RSI: aşırı satım alım fırsatı, aşırı alım risk
    if m.rsi is not None:
        if m.rsi < 30:
            skor += 1
            gerekceler.append(f"RSI {m.rsi}: aşırı satım (tepki yükselişi gelebilir).")
        elif m.rsi > 70:
            skor -= 1
            gerekceler.append(f"RSI {m.rsi}: aşırı alım (geri çekilme riski).")
        else:
            gerekceler.append(f"RSI {m.rsi}: nötr bölge.")

    # 3) MACD histogram: momentum yönü
    if m.macd_hist is not None:
        if m.macd_hist > 0:
            skor += 1
            gerekceler.append("MACD: momentum yukarı (pozitif).")
        elif m.macd_hist < 0:
            skor -= 1
            gerekceler.append("MACD: momentum aşağı (negatif).")

    # 4) Stokastik: aşırı bölgeler
    if m.stokastik is not None:
        if m.stokastik < 20:
            skor += 1
            gerekceler.append(f"Stokastik {m.stokastik}: aşırı satım.")
        elif m.stokastik > 80:
            skor -= 1
            gerekceler.append(f"Stokastik {m.stokastik}: aşırı alım.")

    # 5) Temel sağlık
    if m.saglik_skoru is not None:
        if m.saglik_skoru >= 70:
            skor += 1
            gerekceler.append(f"Şirket sağlığı güçlü ({m.saglik_skoru}/100).")
        elif m.saglik_skoru < 40:
            skor -= 1
            gerekceler.append(f"Şirket sağlığı zayıf ({m.saglik_skoru}/100).")
        else:
            gerekceler.append(f"Şirket sağlığı orta ({m.saglik_skoru}/100).")

    # Yön kararı
    if skor >= 2:
        yon = "Olumlu"
    elif skor <= -2:
        yon = "Zayıf"
    else:
        yon = "Nötr"

    # HESAPLANMIŞ seviyeler (uydurma değil)
    al_alt = m.destek
    al_ust = (m.destek * (Decimal("1") + Decimal("0.03"))).quantize(_IKI_ONDALIK)
    stop = (m.destek * (Decimal("1") - stop_yuzde)).quantize(_IKI_ONDALIK)

    return Yorum(
        yon=yon,
        skor=skor,
        al_bolgesi=(al_alt, al_ust),
        kar_al_hedefi=m.direnc,
        stop_seviyesi=stop,
        gerekceler=gerekceler,
        uyari=_UYARI,
    )


def hisse_yorumu(fiyatlar: list, saglik_skoru: Optional[int] = None, pencere: int = 20) -> Yorum:
    """Fiyat listesinden (ve varsa sağlık skorundan) doğrudan yorum üretir.

    Göstergeleri burada hesaplayıp yorumla()'ya verir. Veri kısa ise ilgili
    göstergeyi atlar (None), motor yine çalışır.
    """
    # Yerel importlar: döngüsel bağımlılık olmasın ve modül hafif kalsın.
    from yatirim.teknik.hareketli_ortalama import basit_hareketli_ortalama
    from yatirim.teknik.rsi import rsi as _rsi
    from yatirim.teknik.macd import macd as _macd
    from yatirim.teknik.stokastik import stokastik_k

    def guvenli(fonk, *a, **k):
        try:
            return fonk(*a, **k)
        except Exception:
            return None

    fiyat = fiyatlar[-1]

    sma_seri = guvenli(basit_hareketli_ortalama, fiyatlar, pencere)
    sma = sma_seri[-1] if sma_seri else None

    rsi_deger = guvenli(_rsi, fiyatlar, 14)

    macd_sonuc = guvenli(_macd, fiyatlar)
    macd_hist = macd_sonuc.histogram[-1] if (macd_sonuc and macd_sonuc.histogram) else None

    stok_seri = guvenli(stokastik_k, fiyatlar, 14)
    stokastik = stok_seri[-1] if stok_seri else None

    # Destek/direnç: son 'pencere' kapanışın en düşük/en yükseği.
    son = fiyatlar[-pencere:] if len(fiyatlar) >= pencere else fiyatlar
    destek = min(son)
    direnc = max(son)

    metrik = MetrikSeti(
        fiyat=fiyat, destek=destek, direnc=direnc,
        sma=sma, rsi=rsi_deger, macd_hist=macd_hist,
        stokastik=stokastik, saglik_skoru=saglik_skoru,
    )
    return yorumla(metrik)
