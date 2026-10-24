"""Pomodoro zil sesi: WAV üretimi ve platforma uyumlu oynatma."""
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave


def generate_pleasant_chime(volume_factor: float = 0.85) -> str:
    temp_dir = tempfile.gettempdir()
    vol_int = int(volume_factor * 100)
    wav_path = os.path.join(temp_dir, f"kavram_chime_v{vol_int}.wav")
    if os.path.exists(wav_path):
        return wav_path

    sample_rate = 44100
    duration = 1.2
    n_samples = int(sample_rate * duration)
    freq1, freq2, freq3 = 659.25, 987.77, 1318.51

    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        envelope = math.exp(-3.5 * t)
        if t < 0.01:
            envelope *= t / 0.01
        val = (0.5 * math.sin(2 * math.pi * freq1 * t)
               + 0.3 * math.sin(2 * math.pi * freq2 * t)
               + 0.2 * math.sin(2 * math.pi * freq3 * t))
        val *= envelope * 0.8 * volume_factor
        samples.append(max(-32768, min(32767, int(val * 32767))))

    try:
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    except Exception as e:
        print(f"Chime WAV generation error: {e}")
    return wav_path


_sound_effect = None


def play_sound_file(wav_path: str, volume: float = 0.85):
    global _sound_effect
    if not os.path.exists(wav_path):
        return

    try:
        from PyQt5.QtMultimedia import QSoundEffect
        from PyQt5.QtCore import QUrl
        if _sound_effect is None:
            _sound_effect = QSoundEffect()
        _sound_effect.setSource(QUrl.fromLocalFile(os.path.abspath(wav_path)))
        _sound_effect.setVolume(volume)
        _sound_effect.play()
        return
    except Exception:
        pass

    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass
    elif sys.platform.startswith("darwin"):
        try:
            subprocess.Popen(["afplay", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
    else:
        for cmd in ["paplay", "aplay", "pw-play", "canberra-gtk-play"]:
            try:
                subprocess.Popen([cmd, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                continue
