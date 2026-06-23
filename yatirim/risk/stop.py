"""Zarar-kes (stop-loss) kuralı.

Bu kural seni en çok koruyan parçadır: her işlemde "buraya gelirse çık"
seviyesini ZORUNLU kılar ve o işlemde kaç para riske attığını hesaplar.

Bu fonksiyon İŞLEM AÇMAZ; sadece öneriyi denetler ve riski sayar.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class ZararKesSonucu:
    """Stop-loss kontrolünün sonucu (sadece bilgi taşır)."""

    uygun: bool                        # Kurala uygun mu?
    riske_atilan: Optional[Decimal]    # Stop'a kadar kaybedebileceğin para.
    ihlaller: list = field(default_factory=list)  # Çiğnenen kuralların açıklamaları.


def zarar_kes_kontrol(
    giris_fiyati: Decimal,
    stop_fiyati: Optional[Decimal],
    adet: Decimal,
    yon: str = "uzun",
) -> ZararKesSonucu:
    """Önerilen işlemde stop-loss kuralını denetler ve riski hesaplar.

    Parametreler
    ------------
    giris_fiyati : Decimal  -> işleme gireceğin fiyat (pozitif olmalı).
    stop_fiyati  : Decimal | None -> "buraya gelirse çık" seviyesi.
                   None ise => stop yok => kural ihlali.
    adet         : Decimal  -> kaç adet/lot (pozitif olmalı).
    yon          : str      -> "uzun" (alım) veya "kisa" (satış).

    Döndürür
    --------
    ZararKesSonucu -> uygun mu, riske atılan para, ihlal listesi.
    """
    # --- Girdi kontrolleri ---
    if giris_fiyati <= 0:
        raise ValueError("giris_fiyati pozitif olmalı.")
    if adet <= 0:
        raise ValueError("adet pozitif olmalı.")
    if yon not in ("uzun", "kisa"):
        raise ValueError("yon yalnızca 'uzun' veya 'kisa' olabilir.")

    # --- Kural 1: stop ZORUNLU ---
    if stop_fiyati is None:
        return ZararKesSonucu(
            uygun=False,
            riske_atilan=None,
            ihlaller=["Stop-loss zorunlu: stop seviyesi olmadan işlem önerilmez."],
        )

    ihlaller = []

    # --- Kural 2: stop doğru tarafta mı? + riski hesapla ---
    if yon == "uzun":
        # Alımda stop, giriş fiyatının ALTINDA olmalı.
        if stop_fiyati >= giris_fiyati:
            ihlaller.append(
                "Uzun (alım) pozisyonda stop, giriş fiyatının altında olmalı."
            )
        riske_atilan = (giris_fiyati - stop_fiyati) * adet
    else:  # yon == "kisa"
        # Satışta stop, giriş fiyatının ÜSTÜNDE olmalı.
        if stop_fiyati <= giris_fiyati:
            ihlaller.append(
                "Kısa (satış) pozisyonda stop, giriş fiyatının üstünde olmalı."
            )
        riske_atilan = (stop_fiyati - giris_fiyati) * adet

    return ZararKesSonucu(
        uygun=(len(ihlaller) == 0),
        riske_atilan=riske_atilan,
        ihlaller=ihlaller,
    )
