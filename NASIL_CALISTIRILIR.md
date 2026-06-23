# YATIRIM — Nasıl Çalıştırılır?

Bu dosya programı kendi bilgisayarında (ve telefonunda) nasıl çalıştıracağını
adım adım anlatır. Komutları **proje kök klasöründe** (bu dosyanın olduğu yerde)
terminalde çalıştır.

---

## 0. Gereksinim
- **Python 3.9 veya üstü** kurulu olmalı. Kontrol:
  ```
  python3 --version
  ```

## 1. Bağımlılıkları kur (canlı veri + web arayüzü için)
```
pip install -r requirements.txt
```
> Not: Sadece hesap mantığı ve testler için kuruluma gerek YOK; bunlar yalın
> Python'la çalışır. yfinance ve streamlit yalnızca canlı veri ve arayüz içindir.

## 2. Testleri çalıştır (her şey yolunda mı?)
```
python3 -m unittest discover -s testler -v
```
Hepsi "ok" / "OK" görünmeli. (Bu testler internet İSTEMEZ.)

## 3. Hızlı örnek (terminalde)
```
python3 ornek_kullanim.py
```

## 4. Web arayüzünü aç (bilgisayarda)
```
streamlit run arayuz/app.py
```
Tarayıcıda otomatik açılır. Sembol gir (örn. `AAPL`, BIST için `THYAO`),
**Analiz Et**'e bas. İlk veri çekme internet ister.

## 5. Telefonda kullan
İki yol var:

**A) Aynı WiFi (en kolay):**
1. Yukarıdaki `streamlit run ...` komutunu bilgisayarında çalıştır.
2. Terminalde **"Network URL"** diye bir adres yazar (örn. `http://192.168.1.20:8501`).
3. Telefonun bilgisayarla **aynı WiFi**'de olsun; bu adresi telefon tarayıcısına yaz.

**B) Her yerden (ücretsiz bulut):**
- Kodu GitHub'a koyup **Streamlit Community Cloud**'a (share.streamlit.io) bağla.
- Tek seferlik kurulum; sonra telefondan her yerden açarsın.
- Bu adımı birlikte ileride yapabiliriz.

---

## Sembol ipuçları
| Piyasa | Örnek sembol |
|---|---|
| ABD hissesi | `AAPL`, `MSFT` |
| BIST (Türk) | `THYAO.IS` (arayüzde `THYAO` yazman yeter) |
| Kripto | `BTC-USD`, `ETH-USD` |
| Altın / Gümüş | `GC=F`, `SI=F` |

## Sık sorulan
- **"yfinance kurulu değil" hatası** → `pip install -r requirements.txt` çalıştır.
- **BIST'te temel veri eksik** → Ücretsiz kaynakta normal; program eksik veriyi
  zarifçe yönetir ("Veri yetersiz" yazar), çökmez.
- **Risk sayılarını değiştirmek** → `yatirim/ayarlar/risk_ayarlari.py`.

> Hatırlatma: Bu araç yalnız ÖNERİ ve UYARI verir. İşlemi ve kararı sen verirsin.
