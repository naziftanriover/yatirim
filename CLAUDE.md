# YATIRIM — Kişisel Yatırım Karar-Destek Programı

Bu dosya projenin **hafızasıdır**: mimari, kurallar ve kaldığımız yer burada tutulur.
Her oturumda önce bu dosya okunur.

> ⚠️ ÇOK ÖNEMLİ: Bu program **asla** işlem açıp kapamaz, parayı otomatik yönetmez.
> SADECE **öneri** ve **uyarı** verir. Kararı ve işlemi kullanıcı (Nazif) yapar.

---

## 1. Amaç
Hisse senetleri, Bitcoin, altın, gümüş ve diğer yatırım araçlarını araştırıp
analiz eden, **öneri + uyarı** veren kişisel bir karar-destek aracı.
Birincil hedef: kullanıcıyı kendi hatasından korumak (özellikle kaldıraç/margin).

## 2. Kapsam (kullanıcı seçimleri)
- **Piyasalar:** BIST (Türk hisseleri), ABD hisseleri, değerli metaller (altın/gümüş), kripto.
- **Para birimi:** Hem TRY hem USD.
- **Dil/teknoloji:** Python.
- **Veri:** Ücretsiz kaynaklar; güncelleme **manuel** (kullanıcı "güncelle" deyince).

## 3. Çalışma Disiplini (değişmez kurallar)
1. Türkçe, kısa-net; her teknik terim açıklanır. Hoca gibi: önce NEDEN/NASIL, sonra onay.
2. Kod yazmadan ÖNCE soru sor, mimariyi anlat, onay bekle.
3. Tek dev dosya YOK. Kod mantıklı modüllere (ayrı dosyalara) bölünür.
4. Her özellik için ÖNCE test, SONRA kod (Test-Önce / TDD).
5. Yeni kod sonrası TÜM testler çalıştırılır (regresyon kontrolü). Testler hep yeşil.
6. Hesaplama mantığı saf, test edilebilir fonksiyonlarda; arayüzden ayrı.
7. Para hesaplarında `Decimal` kullanılır (float değil) — yuvarlama hatasını önlemek için.

## 4. Mimari (klasör yapısı)
```
YATIRIM/
├── CLAUDE.md            ← bu dosya (proje hafızası)
├── ornek_kullanim.py   ← çalışan örnek: tüm parçaları birlikte gösterir
├── yatirim/             ← ana Python paketi (hesap mantığı)
│   ├── risk/            ← 1. RİSK & DİSİPLİN MOTORU  ✅
│   │   ├── pozisyon.py / kaldirac.py / stop.py / toplam.py
│   │   └── kapi.py      ← 4 kuralı tek kararda birleştiren "kapı"
│   ├── veri/            ← 2. veri: csv_okuyucu.py + canli.py (yfinance) ✅
│   ├── temel/           ← 3. temel: oranlar.py + saglik.py (şirket sağlığı) ✅
│   ├── teknik/          ← 4. teknik: hareketli_ortalama, ema, rsi, macd,
│   │                          bollinger, stokastik                ✅
│   ├── tarama/          ← 5. tarama & skorlama (skor.py)          ✅
│   ├── uyari/           ← 6. uyarılar (kosul.py)                  ✅
│   ├── backtest/        ← 7. backtest (calistir.py)              ✅
│   └── ayarlar/         ← kullanıcı risk kuralları (risk_ayarlari.py)
├── arayuz/             ← Streamlit web arayüzü (app.py) — telefon uyumlu
├── requirements.txt    ← dış bağımlılıklar (yfinance, streamlit)
├── NASIL_CALISTIRILIR.md ← kurulum + bilgisayar/telefon çalıştırma rehberi
└── testler/            ← TÜM testler (97 test, hepsi yeşil)
```

### Test çalıştırma
Proje kök klasöründe (`YATIRIM/`):
```
python3 -m unittest discover -s testler -v
```
`pytest` GEREKMEZ. Sadece Python yeterli.

## 5. Risk Motoru — kapsanacak kurallar
- [x] Pozisyon büyüklüğü sınırı: tek işleme toplam paranın en fazla %X'i. ✅ (yatirim/risk/pozisyon.py)
- [x] Kaldıraç kuralı: teminat ana paranın ≤ %20'si, kaldıraç ≤ 5x. ✅ (yatirim/risk/kaldirac.py)
      NOT: Kullanıcı kaldıracı serbest bıraktı ama "%20" = kendi koyduğu para (teminat).
      Bu yüzden stop-loss kuralı bunun yanında ŞART.
- [x] Zarar-kes (stop-loss) zorunluluğu: stop yoksa işlem uygun değil; risk hesaplanır. ✅ (yatirim/risk/stop.py)
- [x] Toplam açık risk tavanı: açık tüm işlemlerin toplam riski tavanı geçemez. ✅ (yatirim/risk/toplam.py)

## 6. Kaldığımız Yer (güncel durum)
- YAYINDA: https://yatirim-borsa.streamlit.app (GitHub naziftanriover/yatirim private + Streamlit Cloud).
- Güncelleme: `bash guncelle.sh "mesaj"`. Veri: yfinance + Stooq yedeği (canli.py).
- AKILLI YORUM: `yatirim/yorum/motor.py` — yön + al bölgesi/kâr-al/stop seviyeleri + gerekçe (tavsiye değil).
- ÖNERİ PANOSU: `yatirim/tarama/panel.py` — izleme listesini tarayıp skora göre sıralar (app.py'de en üstte).
- KAĞIT CÜZDAN: `yatirim/kagit/cuzdan.py` — sahte parayla al-sat (arayüzde session_state).
- Pano açıklaması: app.py'de "Skor nasıl hesaplanıyor?" expander.
- KULLANICI DURUMU: KKTC'de yaşıyor; BTCTurk/Midas TC ikametgâhı istediği için kapalı.
  Sadece Binance Global açık. Bu yüzden gerçek-para işlem zaten zor → kağıt cüzdan öne çıktı.
- SINIR (net): otomatik gerçek al-sat YOK (projenin 1. kuralı + güvenlik). Planlı: Binance SALT-OKUNUR
  (portföy görüntüleme; emir YOK), API anahtarı kullanıcıdan.
- 120 test yeşil. `unittest`. Tüm çekirdek mantık saf + test edilmiş.
- CANLI VERİ eklendi: `yatirim/veri/canli.py` (yfinance) — fiyat geçmişi + temel veri.
  ABD/BIST/kripto/metal. BIST için `bist_sembol()` (.IS eki).
- TEKNİK genişledi: SMA, EMA, RSI, MACD, Bollinger, Stokastik.
- TEMEL genişledi: `saglik.py` — borç/likidite/kârlılık/büyüme/değerleme → 0-100 sağlık
  skoru + güçlü/zayıf yönler. Eksik veriyi zarifçe yönetir.
- WEB ARAYÜZÜ: `arayuz/app.py` (Streamlit), telefon tarayıcısından erişilebilir.
- ÖNEMLİ TEST NOTU: yardımcı ortamda internet YOK; ağ (canli.py) ve arayüz (app.py)
  burada ÇALIŞTIRILARAK test edilemedi — yalnız sözdizimi/parça-mantık doğrulandı.
  Canlı testi kullanıcının makinesinde (`streamlit run arayuz/app.py`).
- OLASI SONRAKİ: (a) Streamlit Cloud'a yükleme (telefondan her yerden),
  (b) fiyat verisini CSV'ye önbellekleme, (c) RSI Wilder yumuşatması,
  (d) backtest'e komisyon/stop ekleme, (e) çoklu sembol tarama ekranı.

## 7. Sözlük (terimler)
- **API:** Veriyi otomatik çekmemizi sağlayan "veri musluğu".
- **Modül:** Programın bir parçası/dosyası.
- **TDD / Test-Önce:** Önce test yaz (kırmızı), sonra geçiren kodu yaz (yeşil), sonra temizle.
- **Regresyon:** Yeni kodun eski çalışan kodu bozması. TÜM testleri çalıştırarak yakalanır.
- **Decimal:** Para için hassas sayı tipi; float'ın yuvarlama hatasını önler.
- **Stop-loss (zarar-kes):** "Fiyat buraya düşerse çık" seviyesi; zararı sınırlar.
- **Kaldıraç/margin:** Borçla işlem; kazancı da zararı da büyütür. Bu projede YASAK.
