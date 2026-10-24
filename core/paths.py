"""Yol çözümleme. Kaynak koddan ve PyInstaller paketinden aynı şekilde çalışır."""
import os
import sys

if getattr(sys, "frozen", False):
    # Paketlenmiş uygulama: kaynaklar _MEIPASS içinde, veri exe'nin yanında.
    RESOURCE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    ENTRY_COMMAND = f'"{sys.executable}"'
else:
    # Kaynak: zaman/ klasörü (bu dosyanın bir üst klasörü).
    RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = RESOURCE_DIR
    ENTRY_COMMAND = f'"{sys.executable}" "{os.path.join(RESOURCE_DIR, "zaman.py")}"'

DATA_DIR = os.path.join(APP_DIR, "veri")
ICON_PATH = os.path.join(RESOURCE_DIR, "ikon", "kavram.png")


def resource_path(relative_path: str) -> str:
    return os.path.join(RESOURCE_DIR, relative_path)
