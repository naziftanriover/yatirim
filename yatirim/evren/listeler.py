"""Hazır sembol listeleri (yfinance biçimi).

- KRIPTO  : majör coinler (X-USD)
- ABD     : ABD büyük şirketleri
- BIST100 : Borsa İstanbul (.IS) — yaklaşık BIST100; zamanla değişebilir.

Not: Ücretsiz veride özellikle BIST'te bazı semboller 'veri yok' dönebilir;
panel bunu zarifçe gösterir.
"""

# --- KRİPTO (majör coinler) ---
KRIPTO = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "BNB-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "DOT-USD", "LINK-USD", "MATIC-USD", "LTC-USD",
    "TRX-USD", "ATOM-USD", "NEAR-USD", "UNI-USD", "AAVE-USD", "FIL-USD",
    "ARB-USD", "OP-USD",
]

# --- ABD büyük şirketleri ---
ABD = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD",
    "NFLX", "INTC", "JPM", "V", "MA", "DIS", "BA", "KO", "PEP", "WMT",
    "XOM", "CVX", "PFE", "JNJ", "UNH", "HD", "CRM", "ORCL", "ADBE",
    "CSCO", "QCOM", "AVGO",
]

# --- BIST100 (yaklaşık; .IS ekli) ---
BIST100 = [
    "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "YKBNK.IS", "VAKBN.IS", "HALKB.IS",
    "SAHOL.IS", "KCHOL.IS", "THYAO.IS", "PGSUS.IS", "TCELL.IS", "TTKOM.IS",
    "BIMAS.IS", "MGROS.IS", "SOKM.IS", "ASELS.IS", "EREGL.IS", "KRDMD.IS",
    "TUPRS.IS", "PETKM.IS", "SISE.IS", "KOZAL.IS", "KOZAA.IS", "FROTO.IS",
    "TOASO.IS", "ARCLK.IS", "VESTL.IS", "TKFEN.IS", "ENKAI.IS", "EKGYO.IS",
    "ALARK.IS", "ASTOR.IS", "ODAS.IS", "AKSEN.IS", "ZOREN.IS", "GUBRF.IS",
    "HEKTS.IS", "KONTR.IS", "SMRTG.IS", "BRYAT.IS", "ISDMR.IS", "OYAKC.IS",
    "CIMSA.IS", "AKCNS.IS", "KARSN.IS", "OTKAR.IS", "DOAS.IS", "TTRAK.IS",
    "ULKER.IS", "AEFES.IS", "CCOLA.IS", "TATGD.IS", "BANVT.IS", "PNSUT.IS",
    "BRISA.IS", "EGEEN.IS", "KORDS.IS", "AKSA.IS", "ALKIM.IS", "BAGFS.IS",
    "DEVA.IS", "ECILC.IS", "SELEC.IS", "LOGO.IS", "NETAS.IS", "INDES.IS",
    "ARENA.IS", "ESEN.IS", "IPEKE.IS", "MAVI.IS", "BIZIM.IS", "CRFSA.IS",
    "DOHOL.IS", "GSDHO.IS", "ISGYO.IS", "KLGYO.IS", "TRGYO.IS", "RYGYO.IS",
    "IZMDC.IS", "KARTN.IS", "KLMSN.IS", "MNDRS.IS", "PARSN.IS", "SARKY.IS",
    "SASA.IS", "TMSN.IS", "VESBE.IS", "YATAS.IS", "GLYHO.IS", "AGHOL.IS",
    "TAVHL.IS", "ENJSA.IS", "AYDEM.IS", "QUAGR.IS", "GWIND.IS", "CANTE.IS",
    "BERA.IS", "ECZYT.IS", "FENER.IS", "GESAN.IS",
]
