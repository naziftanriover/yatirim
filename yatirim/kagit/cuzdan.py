"""Kağıt cüzdan — sahte parayla pozisyon takibi.

KagitCuzdan: başlangıç nakdi tutar, al/sat yapar, pozisyonları ve toplam değeri
izler. Hiçbir gerçek emir göndermez; sadece hafızadaki sayıları günceller.
Para işlemleri Decimal ile yapılır.
"""

from decimal import Decimal

_IKI_ONDALIK = Decimal("0.01")


class KagitCuzdan:
    """Sahte parayla bir portföy. Gerçek para riski yoktur."""

    def __init__(self, baslangic_nakit: Decimal):
        self.baslangic_nakit = Decimal(baslangic_nakit)
        self.nakit = Decimal(baslangic_nakit)
        self.pozisyonlar = {}  # sembol -> adet (Decimal)

    def al(self, sembol: str, fiyat: Decimal, adet: Decimal) -> None:
        """Sahte parayla alım. Nakit yetmiyorsa ValueError."""
        if fiyat <= 0 or adet <= 0:
            raise ValueError("fiyat ve adet pozitif olmalı.")
        maliyet = fiyat * adet
        if maliyet > self.nakit:
            raise ValueError("Yetersiz nakit.")
        self.nakit -= maliyet
        self.pozisyonlar[sembol] = self.pozisyonlar.get(sembol, Decimal("0")) + adet

    def sat(self, sembol: str, fiyat: Decimal, adet: Decimal) -> None:
        """Sahte satış. Elde o kadar pozisyon yoksa ValueError."""
        if fiyat <= 0 or adet <= 0:
            raise ValueError("fiyat ve adet pozitif olmalı.")
        mevcut = self.pozisyonlar.get(sembol, Decimal("0"))
        if adet > mevcut:
            raise ValueError("Yetersiz pozisyon.")
        self.nakit += fiyat * adet
        kalan = mevcut - adet
        if kalan == 0:
            del self.pozisyonlar[sembol]
        else:
            self.pozisyonlar[sembol] = kalan

    def toplam_deger(self, fiyatlar: dict) -> Decimal:
        """Nakit + pozisyonların güncel değeri. fiyatlar: {sembol: fiyat}."""
        deger = self.nakit
        for sembol, adet in self.pozisyonlar.items():
            deger += adet * fiyatlar.get(sembol, Decimal("0"))
        return deger

    def getiri_yuzde(self, fiyatlar: dict) -> Decimal:
        """Başlangıca göre yüzde getiri (2 ondalık)."""
        deger = self.toplam_deger(fiyatlar)
        return ((deger - self.baslangic_nakit) / self.baslangic_nakit
                * Decimal("100")).quantize(_IKI_ONDALIK)
