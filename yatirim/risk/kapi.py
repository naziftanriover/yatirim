"""Risk kapısı — dört kuralı tek kararda birleştirir.

Bir işlem teklifini şu dört kuraldan geçirir:
  1. Tek işlem riski tavanı (pozisyon.py + ayar: max_pozisyon_yuzde)
  2. Kaldıraç/teminat sınırı   (kaldirac.py)
  3. Stop-loss zorunluluğu      (stop.py)
  4. Toplam açık risk tavanı    (toplam.py)

Sonuç: tek bir "UYGUN / UYGUN DEĞİL" + tüm nedenler.
Bu fonksiyon İŞLEM AÇMAZ; sadece öneri/uyarı üretir.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from yatirim.ayarlar.risk_ayarlari import RiskAyarlari, VARSAYILAN
from yatirim.risk.pozisyon import izin_verilen_max_tutar
from yatirim.risk.kaldirac import kaldirac_kontrol
from yatirim.risk.stop import zarar_kes_kontrol
from yatirim.risk.toplam import toplam_risk_kontrol


@dataclass(frozen=True)
class IslemTeklifi:
    """Değerlendirmek istediğin işlem önerisi (girdi)."""

    toplam_sermaye: Decimal
    giris_fiyati: Decimal
    adet: Decimal
    stop_fiyati: Optional[Decimal]
    yon: str = "uzun"
    teminat: Decimal = Decimal("0")          # bu işleme koyduğun kendi paran
    kaldirac_orani: Decimal = Decimal("1")   # 1 = kaldıraçsız
    mevcut_riskler: list = field(default_factory=list)  # açık DİĞER işlemlerin riskleri


@dataclass(frozen=True)
class IslemKarari:
    """Dört kuralın birleşik sonucu (çıktı)."""

    uygun: bool
    riske_atilan: Optional[Decimal]   # bu işlemde stop'a kadar kayıp
    maruziyet: Decimal                # borç dahil gerçek pozisyon büyüklüğü
    toplam_risk: Decimal              # bu işlem dahil tüm açık risk
    ihlaller: list = field(default_factory=list)


def islem_degerlendir(
    teklif: IslemTeklifi,
    ayarlar: RiskAyarlari = VARSAYILAN,
) -> IslemKarari:
    """Bir işlem teklifini dört risk kuralından geçirir ve tek karar döndürür."""
    ihlaller = []

    # --- Kural 3: Stop-loss (riski de buradan öğreniyoruz) ---
    stop_sonuc = zarar_kes_kontrol(
        teklif.giris_fiyati, teklif.stop_fiyati, teklif.adet, teklif.yon
    )
    ihlaller.extend(stop_sonuc.ihlaller)
    riske_atilan = stop_sonuc.riske_atilan

    # --- Kural 1: Tek işlem riski, ana paranın %max_pozisyon_yuzde'sini aşmasın ---
    # (Stop yoksa risk bilinmez; o ihlali zaten yukarıda ekledik.)
    if riske_atilan is not None:
        tek_islem_tavan = izin_verilen_max_tutar(
            teklif.toplam_sermaye, ayarlar.max_pozisyon_yuzde
        )
        if riske_atilan > tek_islem_tavan:
            ihlaller.append(
                f"Tek işlem riski {riske_atilan}; tavan {tek_islem_tavan} "
                f"(ana paranın %{ayarlar.max_pozisyon_yuzde}'si). Adet veya stop mesafesini küçült."
            )

    # --- Kural 2: Kaldıraç/teminat sınırı ---
    kaldirac_sonuc = kaldirac_kontrol(
        teklif.toplam_sermaye, teklif.teminat, teklif.kaldirac_orani, ayarlar
    )
    ihlaller.extend(kaldirac_sonuc.ihlaller)

    # --- Kural 4: Toplam açık risk tavanı (bu işlemin riski dahil) ---
    tum_riskler = list(teklif.mevcut_riskler)
    if riske_atilan is not None:
        tum_riskler.append(riske_atilan)
    toplam_sonuc = toplam_risk_kontrol(teklif.toplam_sermaye, tum_riskler, ayarlar)
    ihlaller.extend(toplam_sonuc.ihlaller)

    return IslemKarari(
        uygun=(len(ihlaller) == 0),
        riske_atilan=riske_atilan,
        maruziyet=kaldirac_sonuc.maruziyet,
        toplam_risk=toplam_sonuc.toplam_risk,
        ihlaller=ihlaller,
    )
