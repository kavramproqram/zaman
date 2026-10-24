"""Global Pomodoro motoru. Sekme ne olursa olsun arka planda çalışır."""
from datetime import timedelta

from PyQt5.QtCore import QObject, pyqtSignal

from core.storage import db, get_now
from core.sound import generate_pleasant_chime, play_sound_file


class PomodoroEngine(QObject):
    tick_signal = pyqtSignal()
    phase_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        cfg = db.data["settings"].get("pomodoro", {})
        self.work_sec = cfg.get("work_min", 25) * 60
        self.short_break_sec = cfg.get("short_break_min", 5) * 60
        self.long_break_sec = cfg.get("long_break_min", 15) * 60
        self.cycles_before_long = 4

        self.phase = "Çalışma"
        self.remaining_seconds = self.work_sec
        self.cycles_done = 0
        self.running = False
        self.target_ts = None
        self.on_alarm_callback = None

    def reset(self):
        self.phase = "Çalışma"
        self.remaining_seconds = self.work_sec
        self.cycles_done = 0
        self.running = False
        self.target_ts = None
        self.tick_signal.emit()

    def start_or_pause(self):
        if not self.running:
            self.running = True
            self.target_ts = get_now() + timedelta(seconds=self.remaining_seconds)
        else:
            self.running = False
            if self.target_ts:
                self.remaining_seconds = max(0, int((self.target_ts - get_now()).total_seconds()))
            self.target_ts = None
        self.tick_signal.emit()

    def tick(self):
        if self.running and self.target_ts:
            secs = (self.target_ts - get_now()).total_seconds()
            if secs <= 0:
                self._next_phase()
            else:
                self.remaining_seconds = int(secs)
        self.tick_signal.emit()

    def _next_phase(self):
        old_phase = self.phase
        active_task_id = db.data["settings"].get("pomodoro", {}).get("active_task_id")
        if old_phase == "Çalışma" and active_task_id:
            db.increment_task_pomo(active_task_id)

        if self.phase == "Çalışma":
            self.cycles_done += 1
            if self.cycles_done % self.cycles_before_long == 0:
                self.phase = "Uzun Mola"
                self.remaining_seconds = self.long_break_sec
            else:
                self.phase = "Kısa Mola"
                self.remaining_seconds = self.short_break_sec
        else:
            self.phase = "Çalışma"
            self.remaining_seconds = self.work_sec

        self.running = False
        self.target_ts = None

        cfg = db.data["settings"].get("pomodoro", {})
        vol = cfg.get("volume", 85) / 100.0
        should_play = cfg.get("sound_enabled", True) and (
            (old_phase == "Çalışma" and cfg.get("sound_work_end", True))
            or (old_phase != "Çalışma" and cfg.get("sound_break_end", True))
        )
        if should_play:
            play_sound_file(generate_pleasant_chime(vol), vol)

        if self.on_alarm_callback:
            self.on_alarm_callback(old_phase, self.phase)
        self.phase_changed_signal.emit(self.phase)
