# GitHub + Streamlit Cloud Yükleme Rehberi

Hedef: Programı **GitHub'a (özel/private)** koymak, sonra **Streamlit Community
Cloud**'a bağlayıp **telefondan her yerden** açılır hale getirmek.

> Neden Firebase değil? Firebase, Python/Streamlit gibi sürekli çalışan bir
> sunucuyu barındıramaz (statik siteler ve küçük fonksiyonlar içindir). Streamlit
> Cloud tam da bizim uygulamamız için yapılmış ve ücretsiz.

Komutları **kendi bilgisayarında Terminal**'de, proje klasöründe çalıştır.

---

## Adım 0 — Git kurulu mu?
```bash
git --version
```
Çıkmazsa macOS "Command Line Tools" kurmayı önerir; onayla.

## Adım 1 — Yarım kalan depoyu temizle ve yeniden başlat
Yardımcı ortam git'i tam bitiremedi (kilit dosyaları kaldı). Senin Mac'inde
yetkin tam olduğu için tek seferde temizleyip baştan başlatıyoruz:
```bash
cd ~/Documents/Claude/Projects/YATIRIM      # klasörün yolu buysa
rm -rf .git                                  # yarım depoyu sil (dosyaların DURUR)
git init -b main
git add -A
git commit -m "İlk sürüm: risk + analiz + canlı veri + web arayüzü"
```

## Adım 2 — GitHub'da ÖZEL depo oluştur
1. github.com → sağ üst **+** → **New repository**.
2. **Repository name:** `yatirim`
3. **Private** seç. (Sadece sen görürsün.)
4. "Add a README" vb. kutuları **İŞARETLEME** (boş depo olsun).
5. **Create repository**.

## Adım 3 — Deponu GitHub'a bağla ve gönder (push)
GitHub'ın verdiği komuta benzer şekilde (KULLANICI_ADIN'ı değiştir):
```bash
git remote add origin https://github.com/KULLANICI_ADIN/yatirim.git
git push -u origin main
```
**Şifre sorulursa:** GitHub artık düz şifre kabul etmiyor; **token** ister.
- github.com → Settings → Developer settings → **Personal access tokens**
  → **Tokens (classic)** → Generate new token → **repo** iznini işaretle → oluştur.
- Token'ı kopyala; push sırasında "password" yerine onu yapıştır.

## Adım 4 — Streamlit Cloud'a deploy et
1. **share.streamlit.io** → **Sign in with GitHub** → izin ver
   (private depo için erişim onayı iste).
2. **Create app** / **New app**.
3. Ayarlar:
   - **Repository:** `KULLANICI_ADIN/yatirim`
   - **Branch:** `main`
   - **Main file path:** `arayuz/app.py`
4. **Deploy!** — `requirements.txt` otomatik kurulur (birkaç dakika sürebilir).
5. Sana bir adres verir (ör. `https://....streamlit.app`).

## Adım 5 — Telefondan aç
Streamlit'in verdiği `.streamlit.app` adresini telefonun tarayıcısında aç.
İstersen ana ekrana kısayol ekle — uygulama gibi durur.

---

## İleride değişiklik yapınca (güncelleme döngüsü)
Kodda bir şey değiştirdiğinde:
```bash
git add -A
git commit -m "ne değiştiğini kısaca yaz"
git push
```
Streamlit Cloud push'u görünce uygulamayı **otomatik** günceller.

## Notlar / olası takılmalar
- **yfinance bulutta bazen yavaş/limitli** olabilir; genelde çalışır, ısrar et.
- **Gizli bilgi koyma:** API anahtarı vb. olursa `.streamlit/secrets.toml`
  kullan; o dosya `.gitignore`'da, GitHub'a gitmez.
- **Özel depo + Streamlit Cloud** ücretsiz planda çalışır; sadece GitHub
  erişim iznini vermen yeterli.
- Takılırsan ekran görüntüsüyle gel, birlikte çözeriz.
