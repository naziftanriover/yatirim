"""ÖRNEK KULLANIM — tüm parçaları birlikte gösterir.

Çalıştırmak için proje kökünde:
    python3 ornek_kullanim.py

Bu dosya bir 'tur' atar: bir işlem teklifini risk kapısından geçirir, teknik ve
temel göstergeleri hesaplar, bir skor verir, uyarı kontrol eder ve küçük bir
backtest yapar. HİÇBİR gerçek işlem açılmaz; sadece öneri/uyarı üretilir.
"""

from decimal import Decimal

from yatirim.risk.kapi import islem_degerlendir, IslemTeklifi
from yatirim.teknik.hareketli_ortalama import basit_hareketli_ortalama
from yatirim.teknik.rsi import rsi
from yatirim.temel.oranlar import fiyat_kazanc, borc_ozkaynak
from yatirim.tarama.skor import hisse_skoru
from yatirim.uyari.kosul import rsi_uyarisi
from yatirim.backtest.calistir import backtest, sma_kesisim_sinyalleri


def cizgi(baslik):
    print("\n" + "=" * 56)
    print(baslik)
    print("=" * 56)


# 1) RİSK KAPISI -----------------------------------------------------------
cizgi("1) RİSK KAPISI — bir işlem teklifini denetle")
teklif = IslemTeklifi(
    toplam_sermaye=Decimal("100000"),
    giris_fiyati=Decimal("100"),
    stop_fiyati=Decimal("98"),
    adet=Decimal("100"),
    yon="uzun",
    teminat=Decimal("10000"),
    kaldirac_orani=Decimal("1"),
    mevcut_riskler=[],
)
karar = islem_degerlendir(teklif)
print(f"Uygun mu? {karar.uygun}")
print(f"Bu işlemde riske atılan: {karar.riske_atilan} TL")
print(f"Toplam açık risk: {karar.toplam_risk} TL")
if karar.ihlaller:
    print("İhlaller:")
    for i in karar.ihlaller:
        print("  -", i)

# Şimdi KÖTÜ bir teklif: çok geniş stop -> tek işlem riski %2'yi aşar
kotu = IslemTeklifi(
    toplam_sermaye=Decimal("100000"),
    giris_fiyati=Decimal("100"),
    stop_fiyati=Decimal("50"),
    adet=Decimal("100"),
    teminat=Decimal("30000"),     # %30 -> teminat ihlali
    kaldirac_orani=Decimal("8"),  # 8x -> kaldıraç ihlali
)
karar2 = islem_degerlendir(kotu)
print(f"\nKötü teklif uygun mu? {karar2.uygun}")
for i in karar2.ihlaller:
    print("  -", i)

# 2) TEKNİK -----------------------------------------------------------------
cizgi("2) TEKNİK — hareketli ortalama ve RSI")
fiyatlar = [Decimal(n) for n in [10, 11, 12, 11, 13, 14, 15, 14, 16, 17]]
print("Son 3 günlük SMA:", basit_hareketli_ortalama(fiyatlar, 3)[-3:])
print("RSI(5):", rsi(fiyatlar, periyot=5))
print("Uyarı:", rsi_uyarisi(rsi(fiyatlar, periyot=5)).mesaj)

# 3) TEMEL + SKOR -----------------------------------------------------------
cizgi("3) TEMEL ORANLAR + SKOR")
fk = fiyat_kazanc(Decimal("100"), Decimal("8"))      # F/K
bo = borc_ozkaynak(Decimal("40"), Decimal("100"))    # Borç/Özkaynak
print(f"F/K: {fk}   Borç/Özkaynak: {bo}")
skor = hisse_skoru(fk=fk, borc_oz=bo, yukari_trend=True, rsi=Decimal("55"))
print(f"Skor: {skor.skor}/100")
for g in skor.gerekceler:
    print("  +", g)

# 4) BACKTEST ---------------------------------------------------------------
cizgi("4) BACKTEST — SMA kesişim stratejisi (sahte para)")
seri = [Decimal(n) for n in [10, 9, 11, 12, 13, 12, 14, 16, 15, 18]]
sinyaller = sma_kesisim_sinyalleri(seri, kisa=2, uzun=4)
sonuc = backtest(seri, sinyaller, Decimal("1000"))
print("Sinyaller:", sinyaller)
print(f"Son değer: {sonuc.son_deger:.2f} TL   "
      f"Getiri: %{sonuc.getiri_yuzde}   İşlem: {sonuc.islem_sayisi}")

print("\nNot: Bunların hepsi ÖNERİ/UYARI. Kararı ve işlemi sen verirsin.")
