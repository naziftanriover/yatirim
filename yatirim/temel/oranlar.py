"""Temel finansal oranlar.

Bu oranlar bir şirketin pahalı/ucuz ya da borçlu olup olmadığını anlamana yarar.
Hepsi saf hesap; 2 ondalığa yuvarlanmış Decimal döndürür.
"""

from decimal import Decimal

_IKI_ONDALIK = Decimal("0.01")


def fiyat_kazanc(fiyat: Decimal, hisse_basi_kazanc: Decimal) -> Decimal:
    """F/K (Fiyat / Kazanç) oranı.

    'Bu şirketin 1 TL kârı için kaç TL ödüyorum?' sorusunu yanıtlar.
    Düşük F/K görece ucuz, yüksek F/K görece pahalı yorumlanır (sektöre göre değişir).

    Hisse başı kazanç (HBK) 0 veya negatifse (şirket zarar ediyorsa) F/K anlamsızdır,
    bu yüzden hata verir.
    """
    if hisse_basi_kazanc <= 0:
        raise ValueError("Hisse başı kazanç pozitif olmalı (zarar varsa F/K anlamsız).")
    return (fiyat / hisse_basi_kazanc).quantize(_IKI_ONDALIK)


def borc_ozkaynak(toplam_borc: Decimal, ozkaynak: Decimal) -> Decimal:
    """Borç / Özkaynak oranı.

    Şirketin kendi parasına (özkaynak) kıyasla ne kadar borçlu olduğunu gösterir.
    Yüksek oran daha riskli demektir. Özkaynak 0 veya negatifse hata verir.
    """
    if ozkaynak <= 0:
        raise ValueError("Özkaynak pozitif olmalı.")
    if toplam_borc < 0:
        raise ValueError("Borç negatif olamaz.")
    return (toplam_borc / ozkaynak).quantize(_IKI_ONDALIK)


def piyasa_defter(fiyat: Decimal, hisse_basi_defter_degeri: Decimal) -> Decimal:
    """PD/DD (Piyasa Değeri / Defter Değeri) oranı.

    Hissenin piyasa fiyatının, muhasebedeki 'defter değerine' oranı.
    1'in altı 'defter değerinin altında işlem görüyor' demektir.
    Defter değeri 0 veya negatifse hata verir.
    """
    if hisse_basi_defter_degeri <= 0:
        raise ValueError("Hisse başı defter değeri pozitif olmalı.")
    return (fiyat / hisse_basi_defter_degeri).quantize(_IKI_ONDALIK)
