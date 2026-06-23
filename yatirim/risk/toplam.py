"""Toplam açık risk tavanı kuralı.

Tek tek her işlem kurallı olsa bile, aynı anda çok sayıda işlem açarsan
toplam riskin tehlikeli olabilir. Bu kural, açık tüm işlemlerin riskini
toplar ve senin tavanını (varsayılan: ana paranın %6'sı) aşıp aşmadığına bakar.

Her işlemin riski = stop.py'deki 'riske_atilan' (giriş ile stop arası kayıp).
Bu fonksiyon İŞLEM AÇMAZ; sadece toplam tabloyu denetler.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from yatirim.ayarlar.risk_ayarlari import RiskAyarlari, VARSAYILAN


@dataclass(frozen=True)
class ToplamRiskSonucu:
    """Toplam risk kontrolünün sonucu (sadece bilgi taşır)."""

    uygun: bool                  # Tavanın altında mı?
    toplam_risk: Decimal         # Açık işlemlerin toplam zarar potansiyeli.
    tavan_tutar: Decimal         # İzin verilen en yüksek toplam risk (para).
    ihlaller: list = field(default_factory=list)


def toplam_risk_kontrol(
    toplam_sermaye: Decimal,
    riskler: list,
    ayarlar: RiskAyarlari = VARSAYILAN,
) -> ToplamRiskSonucu:
    """Açık işlemlerin toplam riskini tavanla karşılaştırır.

    Parametreler
    ------------
    toplam_sermaye : Decimal       -> elindeki toplam para (pozitif olmalı).
    riskler        : list[Decimal] -> her açık işlemin riske attığı para.
                     Yeni bir işlem eklemeyi denerken, onun riskini de bu listeye
                     koyarak "eklersem tavanı aşar mıyım?" sorusunu yanıtlayabilirsin.
    ayarlar        : RiskAyarlari  -> tavan yüzdesi buradan gelir.

    Döndürür
    --------
    ToplamRiskSonucu -> uygun mu, toplam risk, tavan tutarı, ihlal listesi.
    """
    # --- Girdi kontrolleri ---
    if toplam_sermaye <= 0:
        raise ValueError("toplam_sermaye pozitif olmalı.")
    for r in riskler:
        if r < 0:
            raise ValueError("Risk değeri negatif olamaz.")

    # Toplam risk = tüm açık işlem risklerinin toplamı (boşsa 0).
    toplam_risk = sum(riskler, Decimal("0"))

    # Tavan = ana paranın izin verilen yüzdesi.
    tavan_tutar = toplam_sermaye * ayarlar.max_toplam_risk_yuzde / Decimal("100")

    ihlaller = []
    if toplam_risk > tavan_tutar:
        ihlaller.append(
            f"Açık işlemlerin toplam riski {toplam_risk}; "
            f"tavan {tavan_tutar} (ana paranın %{ayarlar.max_toplam_risk_yuzde}'si). "
            f"Yeni işlem açma veya mevcut riski azalt."
        )

    return ToplamRiskSonucu(
        uygun=(len(ihlaller) == 0),
        toplam_risk=toplam_risk,
        tavan_tutar=tavan_tutar,
        ihlaller=ihlaller,
    )
