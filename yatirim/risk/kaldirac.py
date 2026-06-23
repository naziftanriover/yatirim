"""Kaldıraç/margin kuralı.

Nazif'in kuralı:
  - Kaldıraç serbest AMA teminat (kendi koyduğun para) ana paranın en fazla %20'si.
  - En fazla 5x kaldıraç.
Bu sayılar yatirim/ayarlar/risk_ayarlari.py içinde tutulur; istersen oradan değiştirirsin.

Bu fonksiyon İŞLEM AÇMAZ; sadece "bu işlem kurallarına uygun mu?" sorusuna cevap verir.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from yatirim.ayarlar.risk_ayarlari import RiskAyarlari, VARSAYILAN


@dataclass(frozen=True)
class KaldiracSonucu:
    """Kaldıraç kontrolünün sonucu (sadece bilgi taşır, işlem yapmaz)."""

    uygun: bool                       # Kurallara uygun mu?
    maruziyet: Decimal                # Borç dahil gerçek pozisyon büyüklüğü.
    teminat_yuzdesi: Decimal          # Teminatın ana paraya oranı (%).
    ihlaller: list = field(default_factory=list)  # Çiğnenen kuralların açıklamaları.


def kaldirac_kontrol(
    toplam_sermaye: Decimal,
    teminat: Decimal,
    kaldirac_orani: Decimal,
    ayarlar: RiskAyarlari = VARSAYILAN,
) -> KaldiracSonucu:
    """Önerilen kaldıraçlı işlemi risk kurallarına göre denetler.

    Parametreler
    ------------
    toplam_sermaye : Decimal  -> elindeki toplam para (pozitif olmalı).
    teminat        : Decimal  -> bu işleme koyacağın kendi paran (negatif olamaz).
    kaldirac_orani : Decimal  -> 1 = kaldıraçsız, 5 = 5x. 1'in altı olamaz.
    ayarlar        : RiskAyarlari -> sınır değerleri (varsayılan: VARSAYILAN).

    Döndürür
    --------
    KaldiracSonucu  -> uygun mu, maruziyet, teminat yüzdesi, ihlal listesi.
    """
    # --- Girdi kontrolleri (mantıksız değerleri en baştan durdur) ---
    if toplam_sermaye <= 0:
        raise ValueError("toplam_sermaye pozitif olmalı.")
    if teminat < 0:
        raise ValueError("teminat negatif olamaz.")
    if kaldirac_orani < 1:
        raise ValueError("kaldirac_orani 1'den küçük olamaz (1 = kaldıraçsız).")

    ihlaller = []

    # Teminatın ana paraya oranı (%). Örn. 20000 / 100000 * 100 = 20.
    teminat_yuzdesi = teminat / toplam_sermaye * Decimal("100")

    # Kural 1: teminat, ana paranın izin verilen yüzdesini geçemez.
    if teminat_yuzdesi > ayarlar.max_teminat_yuzde:
        ihlaller.append(
            f"Teminat ana paranın %{teminat_yuzdesi}'i; "
            f"sınır %{ayarlar.max_teminat_yuzde}. İşleme koyduğun parayı azalt."
        )

    # Kural 2: kaldıraç oranı izin verilen en yüksek değeri geçemez.
    if kaldirac_orani > ayarlar.max_kaldirac:
        ihlaller.append(
            f"Kaldıraç {kaldirac_orani}x; sınır {ayarlar.max_kaldirac}x. "
            f"Kaldıracı düşür."
        )

    # Maruziyet = borç dahil gerçek pozisyon büyüklüğü = teminat x kaldıraç.
    maruziyet = teminat * kaldirac_orani

    return KaldiracSonucu(
        uygun=(len(ihlaller) == 0),
        maruziyet=maruziyet,
        teminat_yuzdesi=teminat_yuzdesi,
        ihlaller=ihlaller,
    )
