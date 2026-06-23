"""Binance SALT-OKUNUR adaptörü.

Hesabının bakiyelerini OKUR. Emir vermez, para çekmez. (Sadece imzalı GET
/api/v3/account çağrısı yapar.)

Güvenlik:
  - API anahtarı yalnız 'Enable Reading' izinli olmalı (trading/withdraw KAPALI).
  - Anahtar koda yazılmaz; Streamlit secrets'tan gelir.
  - Bu modülde alım/satım/withdraw uç noktası BİLEREK YOKTUR.

İmzalama (imzala/imzali_sorgu) saf ve test edilebilir; ağ çağrısı (bakiye_getir)
internet ister, kullanıcının makinesinde/Cloud'da çalışır.
"""

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from decimal import Decimal
from urllib.parse import urlencode

BINANCE_BASE = "https://api.binance.com"


def imzala(sorgu: str, secret: str) -> str:
    """Sorgu dizesini HMAC-SHA256 ile imzalar (Binance'in beklediği biçim)."""
    return hmac.new(secret.encode(), sorgu.encode(), hashlib.sha256).hexdigest()


def imzali_sorgu(params: dict, secret: str) -> str:
    """Parametreleri sorgu dizesine çevirip sonuna imza ekler."""
    sorgu = urlencode(params)
    return f"{sorgu}&signature={imzala(sorgu, secret)}"


def bakiye_getir(api_key: str, secret: str, *, base: str = BINANCE_BASE,
                 recv_window: int = 5000) -> list:
    """Hesaptaki SIFIRDAN BÜYÜK bakiyeleri döndürür: [(varlık, serbest, kilitli), ...].

    Yalnız okuma yapar. Hata olursa açıklayıcı ValueError verir.
    """
    params = {
        "timestamp": int(time.time() * 1000),
        "recvWindow": recv_window,
    }
    sorgu = imzali_sorgu(params, secret)
    url = f"{base}/api/v3/account?{sorgu}"
    istek = urllib.request.Request(url, headers={"X-MBX-APIKEY": api_key})

    try:
        with urllib.request.urlopen(istek, timeout=15) as cevap:
            veri = json.loads(cevap.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            mesaj = json.loads(e.read().decode("utf-8")).get("msg", str(e))
        except Exception:
            mesaj = str(e)
        raise ValueError(f"Binance hatası: {mesaj}")
    except Exception as e:
        raise ValueError(f"Binance'e bağlanılamadı: {e}")

    bakiyeler = []
    for b in veri.get("balances", []):
        serbest = Decimal(str(b.get("free", "0")))
        kilitli = Decimal(str(b.get("locked", "0")))
        if serbest > 0 or kilitli > 0:
            bakiyeler.append((b.get("asset", "?"), serbest, kilitli))
    # Büyük bakiyeler üstte.
    bakiyeler.sort(key=lambda x: x[1] + x[2], reverse=True)
    return bakiyeler
