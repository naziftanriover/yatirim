"""Emir Özeti — risk kuralına göre hazır emir bilgisi.

Önerilen adedi, klasik '%X risk' kuralından hesaplar: bir işlemde stop'a kadar
kaybın, ana paranın en fazla 'max_pozisyon_yuzde' kadarı olsun.
  önerilen adet = (sermaye * %risk) / (giriş - stop)

Bu fonksiyon EMİR GÖNDERMEZ; sadece sayıları hazırlar.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

from yatirim.ayarlar.risk_ayarlari import RiskAyarlari, VARSAYILAN

_IKI_ONDALIK = Decimal("0.01")


@dataclass(frozen=True)
class EmirOzeti:
    """Kullanıcının elle gireceği hazır emir bilgisi."""

    taraf: str               # öneri: "AL düşünülebilir" / "İZLE / BEKLE"
    giris: Decimal
    stop: Decimal
    kar_al: Decimal
    onerilen_adet: int
    riske_atilan: Decimal
    risk_yuzde: Decimal
    not_: str


def emir_ozeti(
    yon: str,
    toplam_sermaye: Decimal,
    giris: Decimal,
    stop: Decimal,
    kar_al: Decimal,
    ayarlar: RiskAyarlari = VARSAYILAN,
) -> EmirOzeti:
    """Risk kuralına göre hazır emir özeti döndürür (uzun/alım varsayımı).

    Hata: giriş, stop'tan büyük değilse (uzun pozisyonda stop altta olmalı) ValueError.
    """
    if giris <= stop:
        raise ValueError("Uzun pozisyonda giriş, stop'tan büyük olmalı.")
    if toplam_sermaye <= 0:
        raise ValueError("toplam_sermaye pozitif olmalı.")

    birim_risk = giris - stop
    izinli_risk = toplam_sermaye * ayarlar.max_pozisyon_yuzde / Decimal("100")
    # Önerilen adet: tam sayıya AŞAĞI yuvarla (riski aşmamak için).
    onerilen_adet = int((izinli_risk / birim_risk).to_integral_value(rounding=ROUND_DOWN))

    riske_atilan = (Decimal(onerilen_adet) * birim_risk).quantize(_IKI_ONDALIK)
    risk_yuzde = (riske_atilan / toplam_sermaye * Decimal("100")).quantize(_IKI_ONDALIK)

    if yon == "Olumlu":
        taraf = "AL düşünülebilir"
    elif yon == "Zayıf":
        taraf = "ALMA / İZLE (görünüm zayıf)"
    else:
        taraf = "İZLE / BEKLE (sinyal nötr)"

    not_ = ("Bu hazır bir özettir, emir DEĞİLDİR. Emri Binance'te kendi elinle gir; "
            "girişte stop'u da koymayı unutma. Karar senin.")

    return EmirOzeti(
        taraf=taraf, giris=giris, stop=stop, kar_al=kar_al,
        onerilen_adet=onerilen_adet, riske_atilan=riske_atilan,
        risk_yuzde=risk_yuzde, not_=not_,
    )
