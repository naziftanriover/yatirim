"""YATIRIM — Web arayüzü (Streamlit).

Çalıştırma (proje kökünde):
    streamlit run arayuz/app.py

Telefon: bilgisayar ve telefon AYNI WiFi'deyse, Streamlit'in verdiği
'Network URL'yi telefonun tarayıcısına yaz. (Detay: NASIL_CALISTIRILIR.md)

UYARI: Bu araç yalnız ÖNERİ ve UYARI verir. Otomatik işlem AÇMAZ.
Kararı ve işlemi sen verirsin.
"""

import os
import sys
from decimal import Decimal

import streamlit as st

# Proje kökünü (bu dosyanın bir üst klasörü) Python'un arama yoluna ekle.
# Böylece 'streamlit run arayuz/app.py' her ortamda (yerel + Streamlit Cloud)
# 'yatirim' paketini bulabilir.
_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)

from yatirim.veri.canli import fiyat_gecmisi, temel_veri, bist_sembol
from yatirim.teknik.hareketli_ortalama import basit_hareketli_ortalama
from yatirim.teknik.ema import ussel_hareketli_ortalama
from yatirim.teknik.rsi import rsi
from yatirim.teknik.macd import macd
from yatirim.teknik.bollinger import bollinger_bantlari
from yatirim.teknik.stokastik import stokastik_k
from yatirim.temel.saglik import sirket_sagligi
from yatirim.uyari.kosul import rsi_uyarisi
from yatirim.risk.kapi import islem_degerlendir, IslemTeklifi


st.set_page_config(page_title="YATIRIM", page_icon="📊", layout="centered")


def guvenli(fonk, *args, **kw):
    """Bir hesabı çalıştırır; veri yetersizse None döndürür (çökmesin)."""
    try:
        return fonk(*args, **kw)
    except Exception:
        return None


def sembol_duzelt(piyasa: str, kod: str) -> str:
    """Seçilen piyasaya göre sembolü yfinance biçimine getirir."""
    kod = kod.strip()
    if piyasa == "BIST (Türk hisseleri)":
        return bist_sembol(kod)
    return kod.upper()


# --- BAŞLIK ---------------------------------------------------------------
st.title("📊 YATIRIM")
st.caption("Kişisel yatırım karar-destek aracı — sadece öneri ve uyarı verir, "
           "asla otomatik işlem açmaz.")

# --- GİRDİLER -------------------------------------------------------------
piyasa = st.selectbox(
    "Piyasa",
    ["ABD hisseleri", "BIST (Türk hisseleri)", "Kripto", "Değerli metal"],
)
ipucu = {
    "ABD hisseleri": "Örn: AAPL, MSFT",
    "BIST (Türk hisseleri)": "Örn: THYAO, ASELS",
    "Kripto": "Örn: BTC-USD, ETH-USD",
    "Değerli metal": "Örn: GC=F (altın), SI=F (gümüş)",
}[piyasa]
kod = st.text_input("Sembol", placeholder=ipucu)
periyot = st.selectbox("Fiyat geçmişi süresi", ["3mo", "6mo", "1y", "2y", "5y"], index=1)

if st.button("Analiz Et", type="primary") and kod:
    sembol = sembol_duzelt(piyasa, kod)
    with st.spinner(f"{sembol} verisi çekiliyor..."):
        fiyatlar = guvenli(fiyat_gecmisi, sembol, periyot)

    if not fiyatlar:
        st.error(f"'{sembol}' için fiyat verisi alınamadı. Sembolü kontrol et "
                 "veya internet bağlantına bak.")
        st.stop()

    son_fiyat = fiyatlar[-1]
    st.subheader(f"{sembol}")
    st.metric("Son fiyat", f"{son_fiyat:.2f}")
    st.line_chart([float(f) for f in fiyatlar])

    # --- TEKNİK ANALİZ ---------------------------------------------------
    st.markdown("### 📈 Teknik Analiz")
    sma20 = guvenli(basit_hareketli_ortalama, fiyatlar, 20)
    ema20 = guvenli(ussel_hareketli_ortalama, fiyatlar, 20)
    rsi14 = guvenli(rsi, fiyatlar, 14)
    macd_s = guvenli(macd, fiyatlar)
    boll = guvenli(bollinger_bantlari, fiyatlar, 20)
    stok = guvenli(stokastik_k, fiyatlar, 14)

    c1, c2, c3 = st.columns(3)
    c1.metric("SMA(20)", f"{sma20[-1]:.2f}" if sma20 else "—")
    c2.metric("EMA(20)", f"{ema20[-1]:.2f}" if ema20 else "—")
    c3.metric("RSI(14)", f"{rsi14}" if rsi14 is not None else "—")

    if rsi14 is not None:
        st.info("RSI: " + rsi_uyarisi(rsi14).mesaj)

    if macd_s and macd_s.histogram:
        h = macd_s.histogram[-1]
        yon = "yukarı (pozitif)" if h > 0 else "aşağı (negatif)"
        st.write(f"**MACD histogram:** {h:.4f} → momentum {yon}")

    if boll and boll.ust:
        st.write(f"**Bollinger:** alt {boll.alt[-1]:.2f} | "
                 f"orta {boll.orta[-1]:.2f} | üst {boll.ust[-1]:.2f}")
        if son_fiyat >= boll.ust[-1]:
            st.write("→ Fiyat üst banda yakın (görece pahalı/aşırı olabilir).")
        elif son_fiyat <= boll.alt[-1]:
            st.write("→ Fiyat alt banda yakın (görece ucuz/aşırı olabilir).")

    if stok:
        st.write(f"**Stokastik %K:** {stok[-1]}")

    # --- TEMEL ANALİZ ----------------------------------------------------
    st.markdown("### 🏢 Temel Analiz — Şirket Sağlığı")
    tveri = guvenli(temel_veri, sembol)
    if tveri is None:
        st.warning("Temel veri alınamadı (bu sembol için olmayabilir, örn. kripto/metal).")
    else:
        saglik = sirket_sagligi(tveri)
        if saglik.durum == "Veri yetersiz":
            st.warning("Bu sembol için yeterli temel veri yok.")
        else:
            st.metric("Sağlık skoru", f"{saglik.skor}/100", saglik.durum)
            if saglik.guclu:
                st.success("Güçlü yönler:\n- " + "\n- ".join(saglik.guclu))
            if saglik.zayif:
                st.error("Zayıf yönler:\n- " + "\n- ".join(saglik.zayif))

    # --- RİSK KAPISI -----------------------------------------------------
    st.markdown("### 🛡️ Risk Kontrolü (işlem teklifini denetle)")
    with st.form("risk"):
        sermaye = st.number_input("Toplam sermaye", min_value=0.0, value=100000.0, step=1000.0)
        giris = st.number_input("Giriş fiyatı", min_value=0.0, value=float(son_fiyat), step=0.1)
        stop = st.number_input("Stop-loss (zarar-kes)", min_value=0.0, value=float(son_fiyat) * 0.95, step=0.1)
        adet = st.number_input("Adet", min_value=0.0, value=100.0, step=1.0)
        teminat = st.number_input("Bu işleme koyduğun para (teminat)", min_value=0.0, value=10000.0, step=500.0)
        kaldirac = st.number_input("Kaldıraç (1 = yok)", min_value=1.0, value=1.0, step=1.0)
        gonder = st.form_submit_button("Denetle")

    if gonder:
        teklif = IslemTeklifi(
            toplam_sermaye=Decimal(str(sermaye)),
            giris_fiyati=Decimal(str(giris)),
            stop_fiyati=Decimal(str(stop)),
            adet=Decimal(str(adet)),
            yon="uzun",
            teminat=Decimal(str(teminat)),
            kaldirac_orani=Decimal(str(kaldirac)),
            mevcut_riskler=[],
        )
        karar = islem_degerlendir(teklif)
        if karar.uygun:
            st.success(f"UYGUN ✅  | Bu işlemde riske atılan: {karar.riske_atilan:.2f}")
        else:
            st.error("UYGUN DEĞİL ❌")
            for i in karar.ihlaller:
                st.write("- " + i)

st.caption("Geçmiş performans geleceğin garantisi değildir. Kararı sen verirsin.")
