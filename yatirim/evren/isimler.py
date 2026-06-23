"""Sembol -> okunabilir şirket/coin ismi.

Tabloda sembolün yanında isim göstermek için. Bilinmeyen sembol için
ISIMLER.get(sembol, sembol) ile sembolün kendisi gösterilir.
"""

ISIMLER = {
    # --- Kripto ---
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana",
    "AVAX-USD": "Avalanche", "BNB-USD": "BNB", "XRP-USD": "XRP (Ripple)",
    "ADA-USD": "Cardano", "DOGE-USD": "Dogecoin", "DOT-USD": "Polkadot",
    "LINK-USD": "Chainlink", "MATIC-USD": "Polygon", "LTC-USD": "Litecoin",
    "TRX-USD": "TRON", "ATOM-USD": "Cosmos", "NEAR-USD": "NEAR Protocol",
    "UNI-USD": "Uniswap", "AAVE-USD": "Aave", "FIL-USD": "Filecoin",
    "ARB-USD": "Arbitrum", "OP-USD": "Optimism",

    # --- ABD ---
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA",
    "GOOGL": "Alphabet (Google)", "AMZN": "Amazon", "META": "Meta",
    "TSLA": "Tesla", "AMD": "AMD", "NFLX": "Netflix", "INTC": "Intel",
    "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard", "DIS": "Disney",
    "BA": "Boeing", "KO": "Coca-Cola", "PEP": "PepsiCo", "WMT": "Walmart",
    "XOM": "ExxonMobil", "CVX": "Chevron", "PFE": "Pfizer",
    "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "HD": "Home Depot",
    "CRM": "Salesforce", "ORCL": "Oracle", "ADBE": "Adobe", "CSCO": "Cisco",
    "QCOM": "Qualcomm", "AVGO": "Broadcom",

    # --- BIST ---
    "AKBNK.IS": "Akbank", "GARAN.IS": "Garanti BBVA", "ISCTR.IS": "İş Bankası",
    "YKBNK.IS": "Yapı Kredi", "VAKBN.IS": "VakıfBank", "HALKB.IS": "Halkbank",
    "SAHOL.IS": "Sabancı Holding", "KCHOL.IS": "Koç Holding",
    "THYAO.IS": "Türk Hava Yolları", "PGSUS.IS": "Pegasus", "TCELL.IS": "Turkcell",
    "TTKOM.IS": "Türk Telekom", "BIMAS.IS": "BİM", "MGROS.IS": "Migros",
    "SOKM.IS": "Şok Marketler", "ASELS.IS": "Aselsan", "EREGL.IS": "Ereğli Demir Çelik",
    "KRDMD.IS": "Kardemir", "TUPRS.IS": "Tüpraş", "PETKM.IS": "Petkim",
    "SISE.IS": "Şişecam", "KOZAL.IS": "Koza Altın", "KOZAA.IS": "Koza Madencilik",
    "FROTO.IS": "Ford Otosan", "TOASO.IS": "Tofaş", "ARCLK.IS": "Arçelik",
    "VESTL.IS": "Vestel", "TKFEN.IS": "Tekfen Holding", "ENKAI.IS": "Enka İnşaat",
    "EKGYO.IS": "Emlak Konut GYO", "ALARK.IS": "Alarko Holding",
    "ASTOR.IS": "Astor Enerji", "ODAS.IS": "Odaş Elektrik", "AKSEN.IS": "Aksa Enerji",
    "ZOREN.IS": "Zorlu Enerji", "GUBRF.IS": "Gübre Fabrikaları", "HEKTS.IS": "Hektaş",
    "KONTR.IS": "Kontrolmatik", "SMRTG.IS": "Smart Güneş",
    "ISDMR.IS": "İskenderun Demir Çelik", "OYAKC.IS": "Oyak Çimento",
    "CIMSA.IS": "Çimsa", "AKCNS.IS": "Akçansa", "KARSN.IS": "Karsan",
    "OTKAR.IS": "Otokar", "DOAS.IS": "Doğuş Otomotiv", "TTRAK.IS": "Türk Traktör",
    "ULKER.IS": "Ülker", "AEFES.IS": "Anadolu Efes", "CCOLA.IS": "Coca-Cola İçecek",
    "TATGD.IS": "Tat Gıda", "SASA.IS": "Sasa Polyester", "TAVHL.IS": "TAV Havalimanları",
    "ENJSA.IS": "Enerjisa", "AGHOL.IS": "AG Anadolu Grubu", "TMSN.IS": "Tümosan",
    "VESBE.IS": "Vestel Beyaz Eşya", "SELEC.IS": "Selçuk Ecza", "LOGO.IS": "Logo Yazılım",
    "MAVI.IS": "Mavi Giyim", "BIZIM.IS": "Bizim Toptan", "CRFSA.IS": "CarrefourSA",
    "DOHOL.IS": "Doğan Holding", "GLYHO.IS": "Global Yatırım Holding",
    "TRGYO.IS": "Torunlar GYO", "ISGYO.IS": "İş GYO", "BERA.IS": "Bera Holding",
    "FENER.IS": "Fenerbahçe", "GESAN.IS": "Girişim Elektrik", "AKSA.IS": "Aksa Akrilik",
}


def isim(sembol: str) -> str:
    """Sembolün okunabilir ismi; bilinmiyorsa sembolün kendisi."""
    return ISIMLER.get(sembol, sembol)
