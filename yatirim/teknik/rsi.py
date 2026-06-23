"""RSI — Göreceli Güç Endeksi (Relative Strength Index).

RSI, 0-100 arası bir sayıdır. Son 'periyot' günde fiyatın ne kadar
yükseldiğini (kazanç) ne kadar düştüğüne (kayıp) oranlar.
  - 70 üstü genelde 'aşırı alım' (çok yükselmiş, pahalı olabilir),
  - 30 altı genelde 'aşırı satım' (çok düşmüş, ucuz olabilir) yorumlanır.
Bu sadece bir göstergedir; tek başına 'al/sat' kararı verdirmez.

Not: Burada basit ortalama yöntemi kullanılır (Wilder yumuşatması değil) —
öğrenmesi ve test etmesi daha kolay olsun diye.
"""

from decimal import Decimal


def rsi(fiyatlar: list, periyot: int = 14) -> Decimal:
    """Fiyat listesinin EN SON RSI değerini döndürür (2 ondalık).

    En az 'periyot + 1' fiyat gerekir (çünkü değişim = ardışık fark).
    Hata: periyot < 1 ya da yetersiz veri varsa ValueError.
    """
    if periyot < 1:
        raise ValueError("periyot en az 1 olmalı.")
    if len(fiyatlar) < periyot + 1:
        raise ValueError("RSI için en az 'periyot + 1' fiyat gerekir.")

    # Son 'periyot' adetlik fiyat değişimlerini al.
    son_fiyatlar = fiyatlar[-(periyot + 1):]
    kazanclar = Decimal("0")
    kayiplar = Decimal("0")
    for i in range(1, len(son_fiyatlar)):
        degisim = son_fiyatlar[i] - son_fiyatlar[i - 1]
        if degisim > 0:
            kazanclar += degisim
        else:
            kayiplar += -degisim  # kaybı pozitif sayı olarak topla

    ort_kazanc = kazanclar / Decimal(periyot)
    ort_kayip = kayiplar / Decimal(periyot)

    iki_ondalik = Decimal("0.01")

    # Hiç kayıp yoksa RSI = 100 (sürekli yükseliş).
    if ort_kayip == 0:
        return Decimal("100.00")
    # Hiç kazanç yoksa RSI = 0 (sürekli düşüş).
    if ort_kazanc == 0:
        return Decimal("0.00")

    rs = ort_kazanc / ort_kayip
    deger = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    return deger.quantize(iki_ondalik)
