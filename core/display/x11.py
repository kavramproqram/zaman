"""X11 sürücüsü: xrandr (gamma, parlaklık, CTM) ve picom gölgelendirici ile gri mod.

Gri mod sırası:
  1. CTM: xrandr'ın CTM özelliği olan bağlı çıkışlara luma matrisi uygulanır.
     Uygulandığı xrandr --verbose ile doğrulanır.
  2. Picom gölgelendirici: CTM yoksa veya doğrulanamazsa picom ile gri shader çalıştırılır.
  3. İkisi de olmazsa gri mod kurulamaz ve durum satırında bildirilir.
"""
import os
import re
import shutil
import subprocess
import time

from core.display.base import DisplayBackend, has_cmd, run_quiet
from core.paths import DATA_DIR

# xrandr CTM: 9 ondalık değer, satır sırasıyla 3x3 matris (xrandr --verbose ile aynı biçim).
GRAY_MATRIX = [0.2126, 0.7152, 0.0722] * 3
ID_MATRIX = [1, 0, 0, 0, 1, 0, 0, 0, 1]
GRAY_CTM = ",".join(str(v) for v in GRAY_MATRIX)
ID_CTM = ",".join(str(v) for v in ID_MATRIX)

SHADER_FILE = os.path.join(DATA_DIR, "grayscale.glsl")
GRAY_SHADER = """#version 330
in vec2 texcoord;
uniform sampler2D tex;
uniform float opacity;
vec4 default_post_processing(vec4 c);
vec4 window_shader() {
    vec2 sz = textureSize(tex, 0);
    vec4 c  = texture2D(tex, texcoord / sz, 0);
    float g = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
    c = vec4(vec3(g) * opacity, c.a * opacity);
    return default_post_processing(c);
}"""

_OUTPUT_RE = re.compile(r"^(\S+) (connected|disconnected)")


def _parse_verbose(text: str) -> dict:
    """xrandr --verbose çıktısını {çıkış: {connected, ctm}} sözlüğüne çevirir.

    ctm: CTM değerleri (9 sayı) ya da CTM özelliği yoksa None.
    """
    result = {}
    current = None
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        m = _OUTPUT_RE.match(line)
        if m:
            current = m.group(1)
            result[current] = {"connected": m.group(2) == "connected", "ctm": None}
            continue
        if current and line.strip().startswith("CTM:"):
            rows = [line.split("CTM:", 1)[1]]
            j = idx + 1
            # Devam satırları yalnızca sayı içerir; ":" gören satır başka bir özelliktir.
            while len(rows) < 3 and j < len(lines) and lines[j].strip() and ":" not in lines[j]:
                rows.append(lines[j])
                j += 1
            try:
                nums = [float(x) for r in rows for x in r.split()]
            except ValueError:
                continue
            if len(nums) == 9:
                result[current]["ctm"] = nums
    return result


def _matches(nums, target, tol=1e-3) -> bool:
    return bool(nums) and len(nums) == len(target) and all(abs(a - b) < tol for a, b in zip(nums, target))


def _picom_running() -> bool:
    try:
        subprocess.check_output(["pgrep", "-x", "picom"])
        return True
    except Exception:
        return False


class X11Backend(DisplayBackend):
    name = "x11"

    def __init__(self):
        super().__init__()
        self._outputs = None
        self._ctm_outputs = []
        self._picom_was_running = _picom_running()

    def available(self) -> bool:
        return has_cmd("xrandr")

    # ---- çıkışlar (monitörler) ----
    def _verbose(self) -> dict:
        try:
            out = subprocess.check_output(["xrandr", "--verbose"], stderr=subprocess.DEVNULL).decode()
        except Exception:
            return {}
        return _parse_verbose(out)

    def refresh_outputs(self) -> None:
        info = self._verbose()
        self._outputs = [name for name, d in info.items() if d["connected"]]

    def outputs(self):
        if self._outputs is None:
            self.refresh_outputs()
        return self._outputs

    # ---- renk ----
    def set_color(self, r, g, b, brightness) -> None:
        for d in self.outputs():
            run_quiet(["xrandr", "--output", d, "--gamma", f"{r:.2f}:{g:.2f}:{b:.2f}",
                       "--brightness", f"{brightness:.2f}"])

    def reset(self) -> None:
        for d in self.outputs():
            run_quiet(["xrandr", "--output", d, "--gamma", "1.0:1.0:1.0", "--brightness", "1.0"])

    # ---- gri mod ----
    def set_grayscale(self, enable: bool):
        if not enable:
            self._disable_gray()
            return None
        if self.gray_method:
            return self.gray_method
        result = self._enable_ctm()
        if result == "ctm":
            method = "ctm"
        elif result is None:
            # Sistemde hiç CTM özelliği yok: picom gölgelendirici denenir.
            method = self._enable_shader()
        else:
            # CTM var ama uygulanamadı: picom'a geçilmez (gereksiz uyarı ve pencere etkisi olmasın).
            method = None
        print(f"[gri] sonuç: {method or 'başarısız'}", flush=True)
        self.gray_method = method
        return method

    def _set_ctm(self, output: str, value: str) -> bool:
        result = subprocess.run(["xrandr", "--output", output, "--set", "CTM", value],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0

    def _enable_ctm(self):
        """"ctm" döner: uygulandı. "failed": CTM var ama uygulanamadı. None: CTM özelliği yok."""
        info = self._verbose()
        targets = [n for n, d in info.items() if d["connected"] and d["ctm"] is not None]
        print(f"[gri] CTM özelliği olan bağlı çıkışlar: {targets or 'yok'}", flush=True)
        if not targets:
            return None

        ok = True
        for n in targets:
            rc_ok = self._set_ctm(n, GRAY_CTM)
            print(f"[gri] {n} --set CTM: {'tamam' if rc_ok else 'HATA'}", flush=True)
            ok = ok and rc_ok

        # Doğrulama yalnızca bilgi amaçlı; xrandr'ın dönüş kodu asıl karardır.
        after = self._verbose()
        for n in targets:
            current = after.get(n, {}).get("ctm")
            print(f"[gri] {n} sonrası CTM: {current}", flush=True)

        if ok:
            self._ctm_outputs = targets
            return "ctm"
        for n in targets:
            self._set_ctm(n, ID_CTM)
        return "failed"

    def _enable_shader(self):
        if not shutil.which("picom"):
            return None
        try:
            return "shader" if self._apply_shader(True) else None
        except Exception as e:
            print(f"Picom gri shader hatası: {e}")
            return None

    def _disable_gray(self):
        # Önceki oturumdan kalmış bir CTM matrisi varsa da sıfırlanır.
        info = self._verbose()
        for n, d in info.items():
            if d["connected"] and d["ctm"] is not None and not _matches(d["ctm"], ID_MATRIX):
                self._set_ctm(n, ID_CTM)
        if self.gray_method == "shader":
            self._apply_shader(False)
        self._ctm_outputs = []
        self.gray_method = None

    def _apply_shader(self, enable: bool) -> bool:
        os.makedirs(DATA_DIR, exist_ok=True)
        run_quiet(["pkill", "picom"])
        if enable:
            time.sleep(0.2)
            with open(SHADER_FILE, "w") as f:
                f.write(GRAY_SHADER)
            subprocess.Popen(
                ["picom", "--backend", "glx", "--window-shader-fg", SHADER_FILE, "--no-use-damage"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)
            return _picom_running()
        if self._picom_was_running:
            subprocess.Popen(["picom"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return False

    def describe(self) -> str:
        return "X11 (xrandr)"
