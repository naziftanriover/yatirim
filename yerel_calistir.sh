#!/bin/bash
# Uygulamayı KENDİ bilgisayarında çalıştırır.
# (Binance bakiyesi için bu şart: istek senin yerel IP'inden gider, engellenmez.)
# Kullanım:  bash yerel_calistir.sh
set -e
cd "$(dirname "$0")"

# 1) Sanal ortam (ilk seferde kurulur; sistem Python'unu kirletmez)
if [ ! -d ".venv" ]; then
  echo "Sanal ortam kuruluyor (ilk sefer biraz sürebilir)..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2) Gerekli paketleri kur/güncelle
echo "Paketler hazırlanıyor (streamlit, yfinance)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 3) Başlat
echo ""
echo "Uygulama başlıyor. Tarayıcıda açılacak: http://localhost:8501"
echo "Durdurmak için bu pencerede Ctrl+C yap."
echo ""
streamlit run arayuz/app.py
