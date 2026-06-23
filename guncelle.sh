#!/bin/bash
# Değişiklikleri GitHub'a gönderir (Streamlit otomatik yeniden kurar).
# Kullanım:  bash guncelle.sh "ne degistigini kisaca yaz"
cd "$(dirname "$0")"
git add -A
git commit -m "${1:-guncelleme}"
git push
echo "Gönderildi. Streamlit birkaç dakikada uygulamayı yeniler."
