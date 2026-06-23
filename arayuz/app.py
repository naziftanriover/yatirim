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
from yatirim.yorum.motor import hisse_yorumu
from yatirim.tarama.panel import tarama_yap
from yatirim.kagit.cuzdan import KagitCuzdan
from yatirim.borsa.binance_oku import bakiye_getir


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

# --- ÖNERİ PANOSU --------------------------------------------------------
st.markdown("## 📋 Öneri Panosu")
st.caption("İzleme listeni tara; göstergelere göre en güçlü görünenler üste sıralanır. "
           "Bu bir öneri/özettir, yatırım tavsiyesi değildir.")
_VARSAYILAN_LISTE = "AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA"
liste_metni = st.text_area(
    "İzleme listesi (virgül veya satırla ayır; BIST için .IS ekle, örn. THYAO.IS)",
    value=_VARSAYILAN_LISTE, height=80,
)
if st.button("🔎 Önerileri Tara"):
    semboller = [s.strip() for s in liste_metni.replace("\n", ",").split(",") if s.strip()]
    if not semboller:
        st.warning("Önce izleme listesine sembol ekle.")
    else:
        with st.spinner(f"{len(semboller)} sembol taranıyor... (biraz sürebilir)"):
            sonuclar = guvenli(tarama_yap, semboller) or []
        if not sonuclar:
            st.error("Tarama sonuç vermedi. İnternet veya sembolleri kontrol et.")
        else:
            _renk = {"Olumlu": "🟢", "Zayıf": "🔴", "Nötr": "🟡"}
            satirlar = []
            for s in sonuclar:
                if s.hata:
                    satirlar.append({"Sembol": s.sembol, "Görünüm": "⚠️ " + s.hata,
                                     "Skor": "", "Fiyat": "", "Al bölgesi": "",
                                     "Kâr-al": "", "Stop": "", "Sağlık": ""})
                    continue
                satirlar.append({
                    "Sembol": s.sembol,
                    "Görünüm": f"{_renk.get(s.yon, '')} {s.yon}",
                    "Skor": s.skor,
                    "Fiyat": f"{s.fiyat:.2f}" if s.fiyat is not None else "",
                    "Al bölgesi": f"{s.al_alt:.2f}–{s.al_ust:.2f}" if s.al_alt is not None else "",
                    "Kâr-al": f"{s.kar_al:.2f}" if s.kar_al is not None else "",
                    "Stop": f"{s.stop:.2f}" if s.stop is not None else "",
                    "Sağlık": s.saglik_skoru if s.saglik_skoru is not None else "",
                })
            st.dataframe(satirlar, use_container_width=True)
            en_iyi = sonuclar[0]
            if en_iyi.hata is None and en_iyi.yon == "Olumlu":
                st.success(f"En güçlü görünen: {en_iyi.sembol} (skor {en_iyi.skor:+d}). "
                           f"Detay için aşağıdan bu sembolü analiz et.")

with st.expander("ℹ️ Skor nasıl hesaplanıyor?"):
    st.markdown(
        "Her hisseye **5 sinyale** bakılır; her biri **+1 / 0 / −1** puan:\n\n"
        "1. **Trend** — Fiyat 20 günlük ortalamanın üstünde +1, altında −1.\n"
        "2. **RSI** — 30 altı (aşırı satım) +1, 70 üstü (aşırı alım) −1.\n"
        "3. **MACD** — Momentum yukarı +1, aşağı −1.\n"
        "4. **Stokastik** — 20 altı +1, 80 üstü −1.\n"
        "5. **Şirket sağlığı** — Temel skor ≥70 +1, <40 −1.\n\n"
        "Toplam **−5 ile +5** arası. **≥+2 → 🟢 Olumlu**, **≤−2 → 🔴 Zayıf**, "
        "arası **🟡 Nötr**. Tablo bu skora göre sıralanır.\n\n"
        "_Bu bir öneri/özettir, yatırım tavsiyesi değildir; yanılabilir._"
    )

st.markdown("---")
st.markdown("## 🔍 Tek Hisse Analizi")

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
    _sembol = sembol_duzelt(piyasa, kod)
    with st.spinner(f"{_sembol} verisi çekiliyor..."):
        _fiyatlar = guvenli(fiyat_gecmisi, _sembol, periyot)
    if not _fiyatlar:
        st.error(f"'{_sembol}' için fiyat verisi alınamadı. Sembolü kontrol et "
                 "veya internet bağlantına bak.")
    else:
        # Analizi hafızada tut ki butonlara basınca (yeniden çalışınca) kaybolmasın.
        st.session_state["analiz"] = {"sembol": _sembol, "fiyatlar": _fiyatlar}

_analiz = st.session_state.get("analiz")
if _analiz:
    sembol = _analiz["sembol"]
    fiyatlar = _analiz["fiyatlar"]
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
    saglik_skoru = None
    tveri = guvenli(temel_veri, sembol)
    if tveri is None:
        st.warning("Temel veri alınamadı (bu sembol için olmayabilir, örn. kripto/metal).")
    else:
        saglik = sirket_sagligi(tveri)
        if saglik.durum == "Veri yetersiz":
            st.warning("Bu sembol için yeterli temel veri yok.")
        else:
            saglik_skoru = saglik.skor
            st.metric("Sağlık skoru", f"{saglik.skor}/100", saglik.durum)
            if saglik.guclu:
                st.success("Güçlü yönler:\n- " + "\n- ".join(saglik.guclu))
            if saglik.zayif:
                st.error("Zayıf yönler:\n- " + "\n- ".join(saglik.zayif))

    # --- AKILLI YORUM ----------------------------------------------------
    st.markdown("### 🤖 Akıllı Yorum")
    yorum = guvenli(hisse_yorumu, fiyatlar, saglik_skoru)
    if yorum is None:
        st.warning("Yorum üretmek için yeterli veri yok.")
    else:
        renk = {"Olumlu": "🟢", "Zayıf": "🔴", "Nötr": "🟡"}.get(yorum.yon, "")
        st.metric("Genel görünüm", f"{renk} {yorum.yon}", f"sinyal skoru {yorum.skor:+d}")
        a1, a2, a3 = st.columns(3)
        a1.metric("Al bölgesi", f"{yorum.al_bolgesi[0]:.2f}–{yorum.al_bolgesi[1]:.2f}")
        a2.metric("Kâr-al hedefi", f"{yorum.kar_al_hedefi:.2f}")
        a3.metric("Stop seviyesi", f"{yorum.stop_seviyesi:.2f}")
        if yorum.gerekceler:
            st.write("**Gerekçeler:**")
            for g in yorum.gerekceler:
                st.write("- " + g)
        st.warning(yorum.uyari)

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

    # --- KAĞIT CÜZDAN (sahte parayla dene) -------------------------------
    st.markdown("### 📒 Kağıt Cüzdan — sahte parayla dene (gerçek para YOK)")
    if "cuzdan" not in st.session_state:
        st.session_state["cuzdan"] = KagitCuzdan(Decimal("100000"))
    cuzdan = st.session_state["cuzdan"]

    kc_adet = st.number_input("Adet (kağıt işlem)", min_value=0.0, value=10.0, step=1.0)
    al_kol, sat_kol = st.columns(2)
    if al_kol.button(f"📈 Kağıt AL — {sembol} @ {son_fiyat:.2f}"):
        try:
            cuzdan.al(sembol, son_fiyat, Decimal(str(kc_adet)))
            st.success(f"{kc_adet:g} adet {sembol} alındı (sahte).")
        except ValueError as e:
            st.error(str(e))
    if sat_kol.button(f"📉 Kağıt SAT — {sembol} @ {son_fiyat:.2f}"):
        try:
            cuzdan.sat(sembol, son_fiyat, Decimal(str(kc_adet)))
            st.success(f"{kc_adet:g} adet {sembol} satıldı (sahte).")
        except ValueError as e:
            st.error(str(e))

    st.write(f"**Nakit:** {cuzdan.nakit:.2f}")
    if cuzdan.pozisyonlar:
        st.write("**Pozisyonların:**")
        for s, a in cuzdan.pozisyonlar.items():
            ek = f" → bu fiyatla ≈ {(a * son_fiyat):.2f}" if s == sembol else ""
            st.write(f"- {s}: {a:g} adet{ek}")
    else:
        st.write("_Henüz pozisyon yok._")
    if st.button("🔄 Kağıt cüzdanı sıfırla (100.000)"):
        st.session_state["cuzdan"] = KagitCuzdan(Decimal("100000"))
        st.success("Cüzdan sıfırlandı.")

def _gizli(anahtar: str) -> str:
    """Streamlit secrets'tan değer okur; yoksa boş döner (çökmeden)."""
    try:
        return st.secrets.get(anahtar, "")
    except Exception:
        return ""


# --- BINANCE PORTFÖYÜ (SALT-OKUNUR) --------------------------------------
st.markdown("---")
st.markdown("## 🔐 Binance Portföyü (salt-okunur)")
st.caption("Program bakiyeni yalnızca GÖRÜNTÜLER; senin adına ASLA emir vermez, "
           "para çekmez. API anahtarın da yalnız 'okuma' izinli olmalı.")

_bn_key = _gizli("BINANCE_API_KEY")
_bn_secret = _gizli("BINANCE_SECRET")

if not _bn_key or not _bn_secret:
    st.info(
        "Henüz bağlı değil. Bağlamak için:\n\n"
        "1. Binance → API Management → **Create API** → izinlerden SADECE "
        "**Enable Reading** açık olsun (Trading & Withdrawals KAPALI).\n"
        "2. Streamlit uygulaman → **Manage app → Settings → Secrets**'a şunları ekle:\n"
        "```\nBINANCE_API_KEY = \"...\"\nBINANCE_SECRET = \"...\"\n```\n"
        "3. Kaydet; uygulama yenilenince burada **Bakiyemi Getir** butonu çıkar."
    )
else:
    if st.button("💼 Bakiyemi Getir"):
        with st.spinner("Binance'ten bakiye okunuyor..."):
            bakiyeler = guvenli(bakiye_getir, _bn_key, _bn_secret)
        if bakiyeler is None:
            st.error("Bakiye alınamadı. Anahtarı/izinleri ve internet bağlantısını kontrol et.")
        elif not bakiyeler:
            st.info("Hesapta sıfırdan büyük bakiye görünmüyor.")
        else:
            satirlar = [
                {"Varlık": a, "Serbest": f"{s:f}", "Kilitli": f"{k:f}"}
                for a, s, k in bakiyeler
            ]
            st.dataframe(satirlar, use_container_width=True)
            st.caption("Yalnızca görüntüleme. Emir vermek istersen kendi elinle Binance'te yaparsın.")

st.markdown("---")
st.caption("Geçmiş performans geleceğin garantisi değildir. Kararı sen verirsin.")
