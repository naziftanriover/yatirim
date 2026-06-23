#!/bin/bash
# YATIRIM - GitHub'a yükleme yardımcısı
# Çalıştırma (Mac Terminal'de, proje klasöründe):
#     bash github_yukle.sh
#
# ÖNCE: github.com'da BOŞ bir ÖZEL (private) depo aç:
#   github.com -> + -> New repository -> isim: yatirim -> Private
#   -> "Add a README" vb. İŞARETLEME -> Create repository
# Sonra bu betiği çalıştır ve istenen depo URL'sini yapıştır.

set -e
cd "$(dirname "$0")"   # bu betiğin bulunduğu klasör = proje kökü

echo "============================================"
echo "  YATIRIM -> GitHub yükleme"
echo "============================================"

# 1) Git kurulu mu?
if ! command -v git >/dev/null 2>&1; then
  echo "HATA: git kurulu değil. macOS 'Command Line Tools' kurmanı isteyecek; onayla."
  exit 1
fi

# 2) Yarım kalan depoyu temizle, baştan başlat (dosyaların DURUR)
echo "-> Yerel depo hazırlanıyor..."
rm -rf .git
git init -b main >/dev/null
git config user.name "Nazif"
git config user.email "naziftanriover.sb@gmail.com"
git add -A
git commit -m "İlk sürüm: risk + analiz + canlı veri + web arayüzü" >/dev/null
echo "   commit tamam."

# 3) Depo URL'sini al
echo ""
echo "GitHub'da açtığın ÖZEL deponun URL'sini yapıştır."
echo "Örnek: https://github.com/KULLANICI_ADIN/yatirim.git"
read -r -p "Depo URL: " URL

if [ -z "$URL" ]; then
  echo "URL boş. Çıkılıyor. (Depoyu açıp tekrar çalıştır.)"
  exit 1
fi

# 4) Bağla ve gönder
git remote remove origin 2>/dev/null || true
git remote add origin "$URL"
echo ""
echo "-> Gönderiliyor (push)... GitHub kullanıcı adı + TOKEN isteyebilir."
echo "   (Token: github.com -> Settings -> Developer settings ->"
echo "    Personal access tokens (classic) -> 'repo' izniyle oluştur.)"
echo ""
git push -u origin main

echo ""
echo "============================================"
echo "  BİTTİ! Depon GitHub'da."
echo "  Sıradaki: share.streamlit.io -> New app ->"
echo "  Main file path: arayuz/app.py -> Deploy"
echo "============================================"
