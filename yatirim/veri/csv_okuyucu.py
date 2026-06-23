"""CSV fiyat okuyucu.

Borsadan / finans sitesinden indirdiğin fiyat tablosunu (CSV dosyası) okur ve
fiyatları Decimal listesine çevirir. İnternet GEREKMEZ — sen indirir, program okur.

Beklenen CSV biçimi (örnek):
    tarih,kapanis
    2024-01-01,10.5
    2024-01-02,11.0

Sütun adı farklıysa (örn. 'close') 'sutun' parametresiyle belirtirsin.
"""

import csv
from decimal import Decimal, InvalidOperation


def fiyatlari_oku(dosya_yolu: str, sutun: str = "kapanis") -> list:
    """CSV dosyasından belirtilen sütundaki fiyatları sırayla Decimal olarak okur.

    Hatalar
    -------
    FileNotFoundError : dosya yoksa.
    ValueError        : sütun yoksa ya da bir hücre sayıya çevrilemiyorsa.
    """
    fiyatlar = []
    # encoding belirtiyoruz ki Türkçe karakterli dosyalarda sorun olmasın.
    with open(dosya_yolu, "r", encoding="utf-8", newline="") as f:
        okuyucu = csv.DictReader(f)

        # Sütun var mı? (Başlık satırından kontrol et.)
        if okuyucu.fieldnames is None or sutun not in okuyucu.fieldnames:
            raise ValueError(
                f"'{sutun}' sütunu bulunamadı. Mevcut sütunlar: {okuyucu.fieldnames}"
            )

        for satir_no, satir in enumerate(okuyucu, start=2):  # 2: başlık 1. satır
            ham = (satir.get(sutun) or "").strip()
            if ham == "":
                continue  # boş hücreyi atla
            try:
                fiyatlar.append(Decimal(ham))
            except InvalidOperation:
                raise ValueError(
                    f"{satir_no}. satırdaki '{ham}' değeri sayıya çevrilemedi."
                )

    return fiyatlar
