"""Şirket sağlığı değerlendirici (temel analizin kalbi).

Soru: 'Bu şirket sağlam mı? Borcu yönetilebilir mi? Geleceği (büyümesi) var mı?'
Yedi kritere bakar; her birinde veri varsa puanlar, YOKSA o kriteri atlar
(ücretsiz veride bazı alanlar boş gelebilir — program yine de çalışır).

Skor = (geçen kriter / değerlendirilen kriter) * 100.
Durum: >=70 Sağlıklı, 40-69 İzlenmeli, <40 Riskli, hiç veri yoksa 'Veri yetersiz'.

DİKKAT: Bu bir karar değil, bir ÖZET. Yatırım kararını sen verirsin.
Oranların anlamı için bkz. yatirim/temel/oranlar.py.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class TemelVeri:
    """Bir şirketin temel göstergeleri. Eksik alanlar None bırakılır.

    Oranların biçimi:
      fk            : F/K (ör. 12)
      borc_ozkaynak : Borç/Özkaynak ORANI (ör. 0.5 = %50)
      cari_oran     : Dönen varlık / kısa vadeli borç (ör. 2.0)
      roe           : Özkaynak kârlılığı, ondalık (ör. 0.20 = %20)
      net_marj      : Net kâr marjı, ondalık (ör. 0.15 = %15)
      gelir_buyume  : Gelir büyümesi, ondalık (ör. 0.10 = %10)
      kar_buyume    : Kâr büyümesi, ondalık (ör. 0.08 = %8)
    """

    fk: Optional[Decimal] = None
    borc_ozkaynak: Optional[Decimal] = None
    cari_oran: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    net_marj: Optional[Decimal] = None
    gelir_buyume: Optional[Decimal] = None
    kar_buyume: Optional[Decimal] = None


@dataclass(frozen=True)
class SirketSagligi:
    """Sağlık değerlendirmesinin sonucu."""

    skor: int                 # 0-100 (değerlendirilen kriterlere göre)
    durum: str                # Sağlıklı / İzlenmeli / Riskli / Veri yetersiz
    degerlendirilen: int      # kaç kriterde veri vardı
    guclu: list = field(default_factory=list)   # güçlü yönler
    zayif: list = field(default_factory=list)   # zayıf yönler


def sirket_sagligi(
    veri: TemelVeri,
    *,
    fk_tavan: Decimal = Decimal("25"),
    borc_tavan: Decimal = Decimal("1"),
    cari_esik: Decimal = Decimal("1.5"),
    roe_esik: Decimal = Decimal("0.10"),
) -> SirketSagligi:
    """Temel verilere bakıp 0-100 sağlık skoru ve güçlü/zayıf yönleri üretir."""
    guclu, zayif = [], []
    degerlendirilen = 0
    gecen = 0

    def kriter(deger, kosul: bool, iyi_mesaj: str, kotu_mesaj: str):
        """Veri varsa kriteri değerlendirir; yoksa atlar."""
        nonlocal degerlendirilen, gecen
        if deger is None:
            return
        degerlendirilen += 1
        if kosul:
            gecen += 1
            guclu.append(iyi_mesaj)
        else:
            zayif.append(kotu_mesaj)

    # 1) Değerleme: makul F/K (pozitif ve tavanın altında)
    kriter(
        veri.fk, veri.fk is not None and Decimal("0") < veri.fk < fk_tavan,
        f"Makul değerleme (F/K {veri.fk})",
        f"Pahalı ya da zarar (F/K {veri.fk})",
    )
    # 2) Borç: düşük borç/özkaynak
    kriter(
        veri.borc_ozkaynak, veri.borc_ozkaynak is not None and veri.borc_ozkaynak < borc_tavan,
        f"Düşük borç (Borç/Özkaynak {veri.borc_ozkaynak})",
        f"Yüksek borç (Borç/Özkaynak {veri.borc_ozkaynak})",
    )
    # 3) Likidite: kısa vadeli borçları karşılayabilme
    kriter(
        veri.cari_oran, veri.cari_oran is not None and veri.cari_oran > cari_esik,
        f"Güçlü likidite (Cari oran {veri.cari_oran})",
        f"Zayıf likidite (Cari oran {veri.cari_oran})",
    )
    # 4) Kârlılık: özkaynak kârlılığı (ROE)
    kriter(
        veri.roe, veri.roe is not None and veri.roe >= roe_esik,
        f"İyi özkaynak kârlılığı (ROE {veri.roe})",
        f"Düşük özkaynak kârlılığı (ROE {veri.roe})",
    )
    # 5) Kârlılık: net kâr marjı pozitif (kâr ediyor mu)
    kriter(
        veri.net_marj, veri.net_marj is not None and veri.net_marj > 0,
        f"Kâr ediyor (Net marj {veri.net_marj})",
        f"Zarar/çok düşük marj (Net marj {veri.net_marj})",
    )
    # 6) Gelecek: gelir büyümesi pozitif
    kriter(
        veri.gelir_buyume, veri.gelir_buyume is not None and veri.gelir_buyume > 0,
        f"Gelir büyüyor ({veri.gelir_buyume})",
        f"Gelir daralıyor ({veri.gelir_buyume})",
    )
    # 7) Gelecek: kâr büyümesi pozitif
    kriter(
        veri.kar_buyume, veri.kar_buyume is not None and veri.kar_buyume > 0,
        f"Kâr büyüyor ({veri.kar_buyume})",
        f"Kâr daralıyor ({veri.kar_buyume})",
    )

    if degerlendirilen == 0:
        return SirketSagligi(skor=0, durum="Veri yetersiz", degerlendirilen=0)

    skor = round(gecen / degerlendirilen * 100)
    if skor >= 70:
        durum = "Sağlıklı"
    elif skor >= 40:
        durum = "İzlenmeli"
    else:
        durum = "Riskli"

    return SirketSagligi(
        skor=skor, durum=durum, degerlendirilen=degerlendirilen,
        guclu=guclu, zayif=zayif,
    )
