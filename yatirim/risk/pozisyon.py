"""Pozisyon büyüklüğü kuralı.

Tek bir işleme koyabileceğin EN FAZLA parayı hesaplar.
Saf fonksiyon: aynı girdiye hep aynı çıktıyı verir, ekranla/veriyle işi yoktur.
Bu yüzden kolayca test edilir.
"""

from decimal import Decimal


def izin_verilen_max_tutar(toplam_sermaye: Decimal, max_yuzde: Decimal) -> Decimal:
    """Tek işleme ayrılabilecek en fazla tutarı döndürür.

    Parametreler
    ------------
    toplam_sermaye : Decimal
        Elindeki toplam para (negatif olamaz).
    max_yuzde : Decimal
        Tek işleme izin verilen yüzde. Örn. Decimal("2") -> %2.
        0 ile 100 arasında olmalı (100 dahil, 0 hariç).

    Döndürür
    --------
    Decimal
        İzin verilen en fazla para tutarı.

    Hata (ValueError)
    -----------------
    Girdiler mantıksızsa (negatif para, geçersiz yüzde) hata verir.
    Amaç: seni yanlış girdiyle yanlış karardan korumak.
    """
    # --- Girdi kontrolleri (seni koruyan bekçiler) ---
    if toplam_sermaye < 0:
        raise ValueError("toplam_sermaye negatif olamaz.")
    if max_yuzde <= 0:
        raise ValueError("max_yuzde 0'dan büyük olmalı.")
    if max_yuzde > 100:
        raise ValueError("max_yuzde 100'den büyük olamaz (tüm paradan fazlası olmaz).")

    # --- Asıl hesap: paranın 'max_yuzde' kadarı ---
    # yüzde olduğu için 100'e böleriz. Decimal kullandığımız için yuvarlama hatası olmaz.
    return toplam_sermaye * max_yuzde / Decimal("100")
