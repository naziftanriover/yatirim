"""Canlı veri adaptörü (yfinance).

İnternetten fiyat geçmişi ve temel veri çeker. İNCE bir katmandır: yfinance'in
verdiğini bizim sade tiplerimize (Decimal listesi, TemelVeri) çevirir. Böylece
analiz kodu yfinance'i hiç bilmez ve test edilebilir kalır.

ÖNEMLİ:
  - Bu modül internet ister; kendi bilgisayarında çalışır.
  - Kurulum:  pip install yfinance
  - yfinance kurulu değilse, fonksiyonlar açık bir hata mesajı verir.

Sembol ipuçları:
  - ABD hissesi:  "AAPL", "MSFT"
  - BIST hissesi: "THYAO.IS"  (yardımcı: bist_sembol("THYAO"))
  - Kripto:       "BTC-USD", "ETH-USD"
  - Altın/Gümüş:  "GC=F" (altın vadeli), "SI=F" (gümüş vadeli)
"""

from decimal import Decimal
from typing import Optional

from yatirim.temel.saglik import TemelVeri


def _yf():
    """yfinance'i çağrı anında yükler; yoksa anlaşılır hata verir."""
    try:
        import yfinance  # noqa: WPS433 (bilinçli yerel import)
        return yfinance
    except ImportError as e:
        raise ImportError(
            "yfinance kurulu değil. Kurmak için: pip install yfinance"
        ) from e


def _dec(x) -> Optional[Decimal]:
    """Sayıyı güvenle Decimal'e çevirir; None/boş ise None döndürür."""
    if x is None:
        return None
    try:
        # str üzerinden çeviriyoruz ki float yuvarlama hatası girmesin.
        d = Decimal(str(x))
    except Exception:
        return None
    # yfinance bazı alanları NaN verebilir; NaN != NaN özelliğiyle yakala.
    if d != d:
        return None
    return d


def bist_sembol(kod: str) -> str:
    """BIST kodunu yfinance biçimine çevirir: 'THYAO' -> 'THYAO.IS'."""
    kod = kod.strip().upper()
    return kod if kod.endswith(".IS") else f"{kod}.IS"


# periyot -> kaç günlük veri (Stooq yedeği için kabaca kırpma).
_PERIYOT_GUN = {"1mo": 21, "3mo": 63, "6mo": 126, "1y": 252, "2y": 504, "5y": 1260}


def fiyat_gecmisi(sembol: str, periyot: str = "6mo", aralik: str = "1d") -> list:
    """Sembolün kapanış fiyatlarını sırayla Decimal listesi olarak döndürür.

    Önce yfinance (Yahoo) denenir. Bulutta Yahoo engellenirse Stooq'a düşer.

    periyot örnekleri: '1mo','3mo','6mo','1y','2y','5y','max'
    aralik örnekleri:  '1d','1wk','1mo'
    """
    # 1) Birincil kaynak: yfinance (Yahoo)
    try:
        fiyatlar = _yfinance_fiyat(sembol, periyot, aralik)
        if fiyatlar:
            return fiyatlar
    except Exception:
        pass  # yedeğe geç

    # 2) Yedek kaynak: Stooq (özellikle ABD hisseleri; bulut IP'lerini engellemez)
    fiyatlar = _stooq_fiyat(sembol, periyot)
    if fiyatlar:
        return fiyatlar

    raise ValueError(
        f"'{sembol}' için fiyat verisi alınamadı (yfinance ve Stooq denendi)."
    )


def _yfinance_fiyat(sembol: str, periyot: str, aralik: str) -> list:
    """yfinance ile kapanış fiyatlarını çeker."""
    yf = _yf()
    tablo = yf.Ticker(sembol).history(period=periyot, interval=aralik)
    if tablo is None or tablo.empty or "Close" not in tablo.columns:
        return []
    fiyatlar = []
    for x in tablo["Close"].tolist():
        d = _dec(x)
        if d is not None:
            fiyatlar.append(d)
    return fiyatlar


def _stooq_kod(sembol: str):
    """yfinance sembolünü Stooq koduna çevirir; uygun değilse None."""
    s = sembol.strip().lower()
    if s.endswith(".is"):
        return s[:-3] + ".tr"     # BIST (en iyi tahmin)
    if s.endswith("=f"):
        return None               # vadeli (altın/gümüş) -> Stooq farklı, atla
    if "-usd" in s:
        return None               # kripto -> güvenilir eşleme yok, atla
    if "." in s:
        return s                  # zaten son ekli
    return s + ".us"              # ABD hissesi varsay


def _stooq_csv_parse(metin: str, son_n=None) -> list:
    """Stooq CSV metnindeki 'Close' sütununu Decimal listesine çevirir (saf, test edilebilir)."""
    satirlar = metin.strip().splitlines()
    if not satirlar or not satirlar[0].lower().startswith("date"):
        return []
    basliklar = satirlar[0].split(",")
    if "Close" not in basliklar:
        return []
    idx = basliklar.index("Close")

    fiyatlar = []
    for satir in satirlar[1:]:
        parcalar = satir.split(",")
        if len(parcalar) <= idx:
            continue
        ham = parcalar[idx].strip()
        if ham in ("", "N/D"):
            continue
        try:
            fiyatlar.append(Decimal(ham))
        except Exception:
            continue
    if son_n and len(fiyatlar) > son_n:
        fiyatlar = fiyatlar[-son_n:]
    return fiyatlar


def _stooq_fiyat(sembol: str, periyot: str) -> list:
    """Stooq'tan günlük kapanış fiyatlarını çeker (urllib + CSV)."""
    kod = _stooq_kod(sembol)
    if kod is None:
        return []
    url = f"https://stooq.com/q/d/l/?s={kod}&i=d"
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=15) as cevap:
            metin = cevap.read().decode("utf-8", "replace")
    except Exception:
        return []
    return _stooq_csv_parse(metin, _PERIYOT_GUN.get(periyot, 126))


def temel_veri(sembol: str) -> TemelVeri:
    """Sembolün temel göstergelerini TemelVeri olarak döndürür.

    Eksik alanlar None kalır (özellikle BIST'te bazı alanlar boş gelebilir);
    sirket_sagligi bu durumu zaten zarifçe yönetir.
    """
    yf = _yf()
    bilgi = yf.Ticker(sembol).info or {}

    # yfinance debtToEquity'yi YÜZDE verir (50 -> 0.5). Oranımıza çeviriyoruz.
    borc_oz_ham = bilgi.get("debtToEquity")
    borc_oz = _dec(borc_oz_ham)
    if borc_oz is not None:
        borc_oz = borc_oz / Decimal("100")

    return TemelVeri(
        fk=_dec(bilgi.get("trailingPE")),
        borc_ozkaynak=borc_oz,
        cari_oran=_dec(bilgi.get("currentRatio")),
        roe=_dec(bilgi.get("returnOnEquity")),
        net_marj=_dec(bilgi.get("profitMargins")),
        gelir_buyume=_dec(bilgi.get("revenueGrowth")),
        kar_buyume=_dec(bilgi.get("earningsGrowth")),
    )
