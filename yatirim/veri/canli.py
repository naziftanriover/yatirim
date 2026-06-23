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


def fiyat_gecmisi(sembol: str, periyot: str = "6mo", aralik: str = "1d") -> list:
    """Sembolün kapanış fiyatlarını sırayla Decimal listesi olarak döndürür.

    periyot örnekleri: '1mo','3mo','6mo','1y','2y','5y','max'
    aralik örnekleri:  '1d','1wk','1mo'
    """
    yf = _yf()
    tablo = yf.Ticker(sembol).history(period=periyot, interval=aralik)
    if tablo is None or tablo.empty or "Close" not in tablo.columns:
        raise ValueError(f"'{sembol}' için fiyat verisi bulunamadı.")

    fiyatlar = []
    for x in tablo["Close"].tolist():
        d = _dec(x)
        if d is not None:
            fiyatlar.append(d)
    if not fiyatlar:
        raise ValueError(f"'{sembol}' için geçerli kapanış fiyatı yok.")
    return fiyatlar


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
