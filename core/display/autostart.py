"""Oturum açılışında Zaman'ı başlatma (XDG autostart)."""
import os
import sys

from core.paths import ENTRY_COMMAND

AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
DESKTOP_FILE = os.path.join(AUTOSTART_DIR, "kavram_blf.desktop")


def is_enabled() -> bool:
    return os.path.exists(DESKTOP_FILE)


def set_enabled(enabled: bool):
    if enabled:
        os.makedirs(AUTOSTART_DIR, exist_ok=True)
        content = f"""[Desktop Entry]
Type=Application
Exec={ENTRY_COMMAND} --startupHidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Zaman
Comment=Applies custom screen color profile on login"""
        try:
            with open(DESKTOP_FILE, "w") as f:
                f.write(content)
            os.chmod(DESKTOP_FILE, 0o755)
        except Exception as e:
            print("Autostart dosyası oluşturulamadı:", e, file=sys.stderr)
    else:
        if os.path.exists(DESKTOP_FILE):
            try:
                os.remove(DESKTOP_FILE)
            except Exception:
                pass
