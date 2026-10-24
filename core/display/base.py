"""Ekran sürücüsü arayüzü. Her oturum türü bu sınıfı uygular."""
import shutil
import subprocess


def has_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_quiet(args) -> None:
    try:
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass


class DisplayBackend:
    """Sürücü sözleşmesi.

    set_color(r, g, b, brightness): kanal çarpanları (0.1-1.0 civarı) ve parlaklık.
    set_grayscale(enable): "ctm" | "shader" | "gamma" | None (desteklenmiyor) döndürür.
    """
    name = "base"

    def __init__(self):
        self.gray_method = None

    def available(self) -> bool:
        return False

    def refresh_outputs(self) -> None:
        pass

    def set_color(self, r, g, b, brightness) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    def set_grayscale(self, enable: bool):
        return None

    def describe(self) -> str:
        return self.name
