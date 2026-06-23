# YATIRIM — Kişisel Yatırım Karar-Destek Programı

Hisse (BIST + ABD), kripto ve değerli metalleri analiz eden; **öneri ve uyarı**
veren kişisel bir karar-destek aracı. Birincil amaç: kullanıcıyı kendi
hatasından korumak (özellikle kaldıraç/margin riski).

> ⚠️ Bu program **asla** otomatik işlem açmaz, parayı yönetmez.
> Sadece **önerir** ve **uyarır**. Kararı ve işlemi kullanıcı verir.

## Özellikler
- **Risk & Disiplin Motoru:** pozisyon büyüklüğü, kaldıraç/teminat sınırı,
  zarar-kes (stop-loss) zorunluluğu, toplam açık risk tavanı — hepsi tek bir
  "risk kapısı"nda birleşir.
- **Teknik Analiz:** SMA, EMA, RSI, MACD, Bollinger Bantları, Stokastik.
- **Temel Analiz:** F/K, borç/özkaynak, PD/DD oranları + **şirket sağlığı**
  skoru (borç, likidite, kârlılık, büyüme, değerleme → 0-100).
- **Canlı Veri:** yfinance ile fiyat geçmişi ve temel veri (ABD/BIST/kripto/metal).
- **Tarama & Skorlama, Uyarılar, Backtest** (sahte parayla strateji testi).
- **Web Arayüzü:** Streamlit — bilgisayar ve telefon tarayıcısından kullanılabilir.

## Kurulum
```bash
pip install -r requirements.txt
```
> Çekirdek hesap mantığı ve testler bu paketler olmadan da çalışır; yfinance ve
> streamlit yalnızca canlı veri + web arayüzü içindir.

## Çalıştırma
```bash
# Testler (internet gerektirmez)
python3 -m unittest discover -s testler -v

# Terminal örneği
python3 ornek_kullanim.py

# Web arayüzü
streamlit run arayuz/app.py
```
Telefon ve detaylı adımlar için: [NASIL_CALISTIRILIR.md](NASIL_CALISTIRILIR.md)

## Proje yapısı
```
yatirim/   → çekirdek paket (risk, veri, temel, teknik, tarama, uyari, backtest, ayarlar)
arayuz/    → Streamlit web arayüzü
testler/   → 97 test (unittest)
```
Mimari ve kurallar: [CLAUDE.md](CLAUDE.md)

## Teknoloji
Python 3.9+ · unittest · yfinance · streamlit · Decimal (para hassasiyeti)

## Sorumluluk reddi
Bu yazılım yalnızca eğitim ve kişisel karar-destek amaçlıdır. Yatırım tavsiyesi
değildir. Geçmiş performans geleceğin garantisi değildir.
