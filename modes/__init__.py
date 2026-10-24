"""Mod kayıt defteri.

Yeni mod eklemek için:
  1. modes/ klasörüne bir dosya ekleyin ve içine `ModeBase`'den türeyen `Mode` sınıfı yazın.
  2. Aşağıdaki MODULES listesine dosya adını ekleyin. Sıra, menüdeki sırayı belirler.

Bir mod yüklenirken hata verirse uygulama çökmez; o sekmede hata mesajı gösterilir.
"""
import importlib
import traceback

from modes.base import make_error_mode

MODULES = [
    "pomodoro",
    "tasks",
    "notes",
    "calendar_normal",
    "calendar_numeric",
    "calendar_octal",
    "life",
    "date_settings",
    "screen",
    "habits",
]


def load_modes():
    """(modül_adı, sınıf) çiftlerini sırayla döndürür."""
    result = []
    for name in MODULES:
        try:
            module = importlib.import_module(f"modes.{name}")
            result.append((name, module.Mode))
        except Exception:
            result.append((name, make_error_mode(name, traceback.format_exc())))
    return result
