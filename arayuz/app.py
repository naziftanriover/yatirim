"""YATIRIM — Profesyonel panel (Streamlit).

Çalıştırma:
  - Bulut (telefon dahil): yatirim-borsa.streamlit.app
  - Yerel (Binance bakiyesi dahil):  bash yerel_calistir.sh

UYARI: Bu araç yalnız ÖNERİ ve UYARI verir. Otomatik işlem AÇMAZ.
Kararı ve "al/sat" tuşunu hep sen verirsin.
"""

import os
import sys
from decimal import Decimal

import streamlit as st

# Proje kökünü arama yoluna ekle (yerel + Cloud uyumu).
_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)

import pandas as pd

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
from yatirim.borsa.binance_oku import bakiye_getir, binance_islem_linki
from yatirim.emir.ozet import emir_ozeti
from yatirim.evren.listeler import KRIPTO, ABD, BIST100
from yatirim.evren.isimler import isim
import streamlit.components.v1 as components


st.set_page_config(page_title="YATIRIM", page_icon="📊", layout="wide")


# =========================================================================
# Yardımcılar
# =========================================================================
def guvenli(fonk, *args, **kw):
    try:
        return fonk(*args, **kw)
    except Exception:
        return None


def _gizli(anahtar: str) -> str:
    try:
        return st.secrets.get(anahtar, "")
    except Exception:
        return ""


@st.cache_data(ttl=300, show_spinner=False)
def pazar_tara(semboller_tuple, temel_dahil=False, periyot="3mo"):
    """Sembolleri tarayıp tablo için sözlük listesi döndürür (5 dk önbellekli)."""
    sonuc = tarama_yap(list(semboller_tuple), temel_dahil=temel_dahil, periyot=periyot)
    satirlar = []
    for s in sonuc:
        satirlar.append({
            "Sembol": s.sembol,
            "İsim": isim(s.sembol),
            "Fiyat": float(s.fiyat) if s.fiyat is not None else None,
            "Günlük %": float(s.gunluk_degisim) if s.gunluk_degisim is not None else None,
            "Görünüm": s.yon,
            "Skor": s.skor,
            "Al ↓": float(s.al_alt) if s.al_alt is not None else None,
            "Stop": float(s.stop) if s.stop is not None else None,
            "Kâr-al ↑": float(s.kar_al) if s.kar_al is not None else None,
            "_hata": s.hata,
        })
    return satirlar


def _stil(df):
    """Tabloyu renklendir: günlük % yeşil/kırmızı, görünüm renk kodlu."""
    def renk_deg(v):
        if isinstance(v, (int, float)):
            if v > 0:
                return "color: #16a34a; font-weight: 600;"
            if v < 0:
                return "color: #dc2626; font-weight: 600;"
        return ""

    def renk_yon(v):
        return {
            "Olumlu": "background-color: #dcfce7;",
            "Zayıf": "background-color: #fee2e2;",
            "Nötr": "background-color: #fef9c3;",
        }.get(v, "")

    def uygula(styler, fonk, subset):
        # pandas 2.1+ 'map', eski sürümler 'applymap' kullanır.
        if hasattr(styler, "map"):
            return styler.map(fonk, subset=subset)
        return styler.applymap(fonk, subset=subset)

    s = df.style
    s = uygula(s, renk_deg, ["Günlük %"])
    s = uygula(s, renk_yon, ["Görünüm"])
    return s.format({"Fiyat": "{:.2f}", "Günlük %": "{:+.2f}",
                     "Al ↓": "{:.2f}", "Stop": "{:.2f}", "Kâr-al ↑": "{:.2f}"},
                    na_rep="—")


def pazar_paneli(baslik, semboller, anahtar, temel_dahil=False):
    """Bir piyasa panelini çizer: Tara butonu + renkli fiyat/sinyal tablosu."""
    st.markdown(f"#### {baslik}  ·  {len(semboller)} sembol")
    ust = st.columns([1, 2, 2])
    if ust[0].button("🔄 Tara / Yenile", key=f"btn_{anahtar}", type="primary"):
        with st.spinner(f"{len(semboller)} sembol taranıyor... (biraz sürebilir)"):
            st.session_state[f"sonuc_{anahtar}"] = guvenli(
                pazar_tara, tuple(semboller), temel_dahil, "3mo") or []

    sonuc = st.session_state.get(f"sonuc_{anahtar}")
    if sonuc is None:
        st.info("Fiyatları ve önerileri görmek için **Tara / Yenile**'ye bas.")
        return
    if not sonuc:
        st.error("Tarama sonuç vermedi. İnternet veya sembolleri kontrol et.")
        return

    df = pd.DataFrame(sonuc)
    df_ok = df[df["_hata"].isna()].drop(columns=["_hata"])
    df_err = df[df["_hata"].notna()]

    # Özet metrikler
    olumlu = int((df_ok["Görünüm"] == "Olumlu").sum())
    zayif = int((df_ok["Görünüm"] == "Zayıf").sum())
    m = st.columns(3)
    m[0].metric("🟢 Olumlu", olumlu)
    m[1].metric("🔴 Zayıf", zayif)
    m[2].metric("Veri gelen / toplam", f"{len(df_ok)} / {len(df)}")

    if not df_ok.empty:
        st.dataframe(_stil(df_ok), use_container_width=True, hide_index=True)
    if not df_err.empty:
        with st.expander(f"Veri gelmeyen {len(df_err)} sembol"):
            st.write(", ".join(df_err["Sembol"].tolist()))
    st.caption("Skor 5 sinyalden gelir (trend, RSI, MACD, Stokastik, sağlık). "
               "Öneri/özettir, yatırım tavsiyesi değildir.")
    detay_secimi(sonuc, anahtar)


def detay_secimi(sonuc, anahtar):
    """Tablonun altına 'şirket/coin verisi gör' seçim kutusu koyar."""
    secenekler = [f'{r["Sembol"]} — {r.get("İsim", "")}'.strip(" —")
                  for r in sonuc if not r.get("_hata")]
    if not secenekler:
        return
    secim = st.selectbox("🔎 Şirket/coin verisini gör", ["—"] + secenekler,
                         key=f"sec_{anahtar}")
    if secim and secim != "—":
        detay_goster(secim.split(" — ")[0])


def detay_goster(sembol):
    """Seçilen sembol için temel/şirket verisini gösterir."""
    with st.spinner(f"{sembol} verisi çekiliyor..."):
        tveri = guvenli(temel_veri, sembol)
    st.markdown(f"**{isim(sembol)}** ({sembol})")
    if tveri is not None:
        sg = sirket_sagligi(tveri)
        if sg.durum != "Veri yetersiz":
            st.metric("Şirket sağlığı", f"{sg.skor}/100", sg.durum)
            if sg.guclu:
                st.success("Güçlü: " + ", ".join(sg.guclu))
            if sg.zayif:
                st.error("Zayıf: " + ", ".join(sg.zayif))
            st.caption("Grafik + tüm göstergeler için sembolü '🔍 Tek Analiz'e yaz.")
            return
    st.info("Bu sembolde temel veri yok/yetersiz (kripto/metal olabilir). "
            "Tam analiz için '🔍 Tek Analiz' sekmesini kullan.")


def ticker_ciz():
    """Üstte akan canlı fiyat şeridi (majör coinler)."""
    semboller = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD",
                 "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL"]
    veri = guvenli(pazar_tara, tuple(semboller), False, "1mo") or []
    parcalar = []
    for r in veri:
        if r.get("_hata") or r.get("Fiyat") is None:
            continue
        deg = r.get("Günlük %") or 0.0
        renk = "#22c55e" if deg >= 0 else "#ef4444"
        ok = "▲" if deg >= 0 else "▼"
        ad = r["Sembol"].replace("-USD", "")
        parcalar.append(
            f'<span style="margin:0 26px;">{ad} '
            f'<b>{r["Fiyat"]:.2f}</b> '
            f'<span style="color:{renk}">{ok} {abs(deg):.2f}%</span></span>'
        )
    if not parcalar:
        return
    icerik = "".join(parcalar)
    html = (
        '<div style="overflow:hidden;white-space:nowrap;background:#0f172a;'
        'color:#e5e7eb;border-radius:10px;padding:10px 0;font-family:sans-serif;'
        'font-size:15px;">'
        '<div style="display:inline-block;padding-left:100%;'
        'animation:kay 28s linear infinite;">' + icerik + icerik + '</div></div>'
        '<style>@keyframes kay{0%{transform:translateX(0)}'
        '100%{transform:translateX(-50%)}}</style>'
    )
    components.html(html, height=46)


# =========================================================================
# Başlık
# =========================================================================
st.title("📊 YATIRIM")
st.caption("Kişisel yatırım karar-destek paneli — öneri ve uyarı verir, asla otomatik işlem açmaz.")
ticker_ciz()

sekme_oneri, sekme_kripto, sekme_bist, sekme_abd, sekme_analiz, sekme_binance = st.tabs(
    ["📋 Öneriler", "🪙 Kripto", "🇹🇷 BIST", "🇺🇸 ABD", "🔍 Tek Analiz", "🔐 Binance"]
)


# =========================================================================
# SEKME: ÖNERİLER (kripto + ABD birleşik en güçlüler)
# =========================================================================
with sekme_oneri:
    st.markdown("### 📋 Öneri Panosu")
    st.caption("Kripto + ABD taranır, sinyale göre en güçlü görünenler üste gelir.")
    if st.button("🔎 Önerileri Tara", key="btn_oneri", type="primary"):
        evren = tuple(KRIPTO + ABD)
        with st.spinner(f"{len(evren)} sembol taranıyor... (biraz sürebilir)"):
            st.session_state["sonuc_oneri"] = guvenli(pazar_tara, evren, False, "3mo") or []

    sonuc = st.session_state.get("sonuc_oneri")
    if sonuc is None:
        st.info("Sana önerilen coin ve hisseleri görmek için **Önerileri Tara**'ya bas.")
    elif not sonuc:
        st.error("Tarama sonuç vermedi.")
    else:
        df = pd.DataFrame(sonuc)
        df_ok = df[df["_hata"].isna()].drop(columns=["_hata"])
        st.markdown("#### 🟢 En güçlü görünen ilk 15")
        st.dataframe(_stil(df_ok.head(15)), use_container_width=True, hide_index=True)
        st.caption("Detaylı bakmak için sembolü '🔍 Tek Analiz' sekmesine yaz.")
        detay_secimi(df_ok.head(15).to_dict("records"), "oneri")


# =========================================================================
# SEKME: KRİPTO / BIST / ABD panelleri
# =========================================================================
with sekme_kripto:
    pazar_paneli("🪙 Kripto", KRIPTO, "kripto", temel_dahil=False)

with sekme_bist:
    st.warning("BIST100 taraması yavaştır ve ücretsiz veride bazı hisseler 'veri yok' "
               "dönebilir. Sabırla bekle.")
    pazar_paneli("🇹🇷 BIST100", BIST100, "bist", temel_dahil=False)

with sekme_abd:
    pazar_paneli("🇺🇸 ABD", ABD, "abd", temel_dahil=False)


# =========================================================================
# SEKME: TEK HİSSE ANALİZİ (detaylı)
# =========================================================================
with sekme_analiz:
    st.markdown("### 🔍 Tek Hisse / Coin Analizi")
    g = st.columns([2, 3, 2])
    piyasa = g[0].selectbox("Piyasa", ["ABD hisseleri", "BIST (Türk hisseleri)", "Kripto", "Değerli metal"])
    ipucu = {
        "ABD hisseleri": "Örn: AAPL",
        "BIST (Türk hisseleri)": "Örn: THYAO",
        "Kripto": "Örn: BTC-USD",
        "Değerli metal": "Örn: GC=F",
    }[piyasa]
    kod = g[1].text_input("Sembol", placeholder=ipucu)
    periyot = g[2].selectbox("Süre", ["3mo", "6mo", "1y", "2y", "5y"], index=1)

    def sembol_duzelt(piyasa, kod):
        kod = kod.strip()
        if piyasa == "BIST (Türk hisseleri)":
            return bist_sembol(kod)
        return kod.upper()

    if st.button("Analiz Et", type="primary", key="analiz_btn") and kod:
        _sembol = sembol_duzelt(piyasa, kod)
        with st.spinner(f"{_sembol} verisi çekiliyor..."):
            _fiyatlar = guvenli(fiyat_gecmisi, _sembol, periyot)
        if not _fiyatlar:
            st.error(f"'{_sembol}' için fiyat verisi alınamadı.")
        else:
            st.session_state["analiz"] = {"sembol": _sembol, "fiyatlar": _fiyatlar}

    _analiz = st.session_state.get("analiz")
    if _analiz:
        sembol = _analiz["sembol"]
        fiyatlar = _analiz["fiyatlar"]
        son_fiyat = fiyatlar[-1]
        st.subheader(sembol)
        st.metric("Son fiyat", f"{son_fiyat:.2f}")
        st.line_chart([float(f) for f in fiyatlar])

        # Teknik
        st.markdown("#### 📈 Teknik Analiz")
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
            st.write(f"**MACD histogram:** {h:.4f} → momentum "
                     f"{'yukarı' if h > 0 else 'aşağı'}")
        if boll and boll.ust:
            st.write(f"**Bollinger:** alt {boll.alt[-1]:.2f} | orta {boll.orta[-1]:.2f} "
                     f"| üst {boll.ust[-1]:.2f}")
        if stok:
            st.write(f"**Stokastik %K:** {stok[-1]}")

        # Temel
        st.markdown("#### 🏢 Şirket Sağlığı")
        saglik_skoru = None
        tveri = guvenli(temel_veri, sembol)
        if tveri is None:
            st.warning("Temel veri yok (kripto/metal olabilir).")
        else:
            saglik = sirket_sagligi(tveri)
            if saglik.durum == "Veri yetersiz":
                st.warning("Bu sembol için yeterli temel veri yok.")
            else:
                saglik_skoru = saglik.skor
                st.metric("Sağlık skoru", f"{saglik.skor}/100", saglik.durum)
                if saglik.guclu:
                    st.success("Güçlü: " + ", ".join(saglik.guclu))
                if saglik.zayif:
                    st.error("Zayıf: " + ", ".join(saglik.zayif))

        # Akıllı yorum + emir özeti
        st.markdown("#### 🤖 Akıllı Yorum")
        yorum = guvenli(hisse_yorumu, fiyatlar, saglik_skoru)
        if yorum is None:
            st.warning("Yorum için yeterli veri yok.")
        else:
            renk = {"Olumlu": "🟢", "Zayıf": "🔴", "Nötr": "🟡"}.get(yorum.yon, "")
            st.metric("Genel görünüm", f"{renk} {yorum.yon}", f"sinyal skoru {yorum.skor:+d}")
            a1, a2, a3 = st.columns(3)
            a1.metric("Al bölgesi", f"{yorum.al_bolgesi[0]:.2f}–{yorum.al_bolgesi[1]:.2f}")
            a2.metric("Kâr-al hedefi", f"{yorum.kar_al_hedefi:.2f}")
            a3.metric("Stop", f"{yorum.stop_seviyesi:.2f}")
            for gx in yorum.gerekceler:
                st.write("- " + gx)
            st.warning(yorum.uyari)

            st.markdown("#### 📝 Emir Özeti — hazır; emri SEN verirsin")
            sermaye = st.number_input("Toplam sermayen", min_value=0.0, value=100000.0,
                                      step=1000.0, key="emir_sermaye")
            ozet = guvenli(emir_ozeti, yorum.yon, Decimal(str(sermaye)), son_fiyat,
                           yorum.stop_seviyesi, yorum.kar_al_hedefi)
            if ozet is not None:
                st.write(f"**Öneri:** {ozet.taraf}  ·  **Önerilen adet:** {ozet.onerilen_adet}  "
                         f"(riske atılan ≈ {ozet.riske_atilan}, ana paranın %{ozet.risk_yuzde}'i)")
                _link = binance_islem_linki(sembol)
                if _link:
                    st.link_button("🔗 Binance'te işlem sayfasını aç", _link)
                st.info(ozet.not_)

        # Risk kapısı
        st.markdown("#### 🛡️ Risk Kontrolü")
        with st.form("risk"):
            r = st.columns(3)
            sermaye2 = r[0].number_input("Sermaye", min_value=0.0, value=100000.0, step=1000.0)
            giris = r[1].number_input("Giriş", min_value=0.0, value=float(son_fiyat), step=0.1)
            stop = r[2].number_input("Stop", min_value=0.0, value=float(son_fiyat) * 0.95, step=0.1)
            r2 = st.columns(3)
            adet = r2[0].number_input("Adet", min_value=0.0, value=100.0, step=1.0)
            teminat = r2[1].number_input("Teminat", min_value=0.0, value=10000.0, step=500.0)
            kaldirac = r2[2].number_input("Kaldıraç (1=yok)", min_value=1.0, value=1.0, step=1.0)
            gonder = st.form_submit_button("Denetle")
        if gonder:
            karar = islem_degerlendir(IslemTeklifi(
                toplam_sermaye=Decimal(str(sermaye2)), giris_fiyati=Decimal(str(giris)),
                stop_fiyati=Decimal(str(stop)), adet=Decimal(str(adet)), yon="uzun",
                teminat=Decimal(str(teminat)), kaldirac_orani=Decimal(str(kaldirac)),
                mevcut_riskler=[]))
            if karar.uygun:
                st.success(f"UYGUN ✅ | riske atılan: {karar.riske_atilan:.2f}")
            else:
                st.error("UYGUN DEĞİL ❌")
                for i in karar.ihlaller:
                    st.write("- " + i)

        # Kağıt cüzdan
        st.markdown("#### 📒 Kağıt Cüzdan — sahte parayla dene")
        if "cuzdan" not in st.session_state:
            st.session_state["cuzdan"] = KagitCuzdan(Decimal("100000"))
        cuzdan = st.session_state["cuzdan"]
        kc_adet = st.number_input("Adet (kağıt)", min_value=0.0, value=10.0, step=1.0)
        kcol = st.columns(2)
        if kcol[0].button(f"📈 Kağıt AL @ {son_fiyat:.2f}"):
            try:
                cuzdan.al(sembol, son_fiyat, Decimal(str(kc_adet)))
                st.success("Alındı (sahte).")
            except ValueError as e:
                st.error(str(e))
        if kcol[1].button(f"📉 Kağıt SAT @ {son_fiyat:.2f}"):
            try:
                cuzdan.sat(sembol, son_fiyat, Decimal(str(kc_adet)))
                st.success("Satıldı (sahte).")
            except ValueError as e:
                st.error(str(e))
        st.write(f"**Nakit:** {cuzdan.nakit:.2f}")
        if cuzdan.pozisyonlar:
            st.write("**Pozisyonlar:** " + ", ".join(
                f"{s}: {a:g}" for s, a in cuzdan.pozisyonlar.items()))


# =========================================================================
# SEKME: BINANCE (salt-okunur)
# =========================================================================
with sekme_binance:
    st.markdown("### 🔐 Binance Portföyü (salt-okunur)")
    st.caption("Program bakiyeni yalnızca GÖRÜNTÜLER; senin adına ASLA emir vermez, para çekmez.")
    _bn_key = _gizli("BINANCE_API_KEY")
    _bn_secret = _gizli("BINANCE_SECRET")
    if not _bn_key or not _bn_secret:
        st.info("Henüz bağlı değil. Binance'te SADECE 'Enable Reading' izinli bir API anahtarı "
                "oluştur, sonra anahtarları Streamlit Secrets'a (yerelde .streamlit/secrets.toml) ekle.")
    else:
        if st.button("💼 Bakiyemi Getir", type="primary"):
            try:
                with st.spinner("Binance'ten okunuyor..."):
                    bakiyeler = bakiye_getir(_bn_key, _bn_secret)
                if not bakiyeler:
                    st.info("Sıfırdan büyük bakiye görünmüyor.")
                else:
                    st.dataframe(
                        [{"Varlık": a, "Serbest": f"{s:f}", "Kilitli": f"{k:f}"}
                         for a, s, k in bakiyeler],
                        use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Bakiye alınamadı: {e}")
                if "restricted" in str(e).lower() or "451" in str(e):
                    st.warning("Coğrafi engel: Streamlit Cloud (ABD) Binance'e kapalı. "
                               "Uygulamayı kendi bilgisayarında çalıştır (bash yerel_calistir.sh).")

st.markdown("---")
st.caption("Geçmiş performans geleceğin garantisi değildir. Otomatik işlem yok; kararı sen verirsin.")
