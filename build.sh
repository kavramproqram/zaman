#!/usr/bin/env bash
# Tek dosyalık çalıştırılabilir paket üretir: dist/zaman
# Gereksinim: Python 3.9+ ve bu platformda derleme (paket, üretildiği sistemde çalışır).
set -euo pipefail

# Yol adında Türkçe karakter (İ, ş, ğ...) varsa PyInstaller Qt eklentilerini bulamaz;
# UTF-8 locale bunu önler.
export LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONUTF8=1

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PY="${PYTHON:-python3}"
if [ ! -x .venv/bin/python ]; then
    "$PY" -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt pyinstaller
.venv/bin/python -m PyInstaller --version >/dev/null 2>&1 || {
    echo "[build] HATA: PyInstaller kurulamadı. Yukarıdaki pip çıktısına bakın." >&2
    exit 1
}

SEP=":"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) SEP=";" ;; esac

rm -rf build dist zaman.spec

# ikon klasörü varsa pakete ekle; yoksa uygulama ikonsuz çalışır.
ADD_DATA=()
if [ -d ikon ]; then
    ADD_DATA=(--add-data "ikon${SEP}ikon")
fi

.venv/bin/python -m PyInstaller --noconfirm --onefile --name zaman \
    "${ADD_DATA[@]}" \
    --hidden-import modes.pomodoro --hidden-import modes.tasks --hidden-import modes.notes \
    --hidden-import modes.calendar_normal --hidden-import modes.calendar_numeric \
    --hidden-import modes.calendar_octal --hidden-import modes.life \
    --hidden-import modes.date_settings --hidden-import modes.screen --hidden-import modes.habits \
    zaman.py

chmod +x dist/zaman
echo "[build] Hazır: $DIR/dist/zaman"
