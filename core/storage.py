"""Kalıcı veri (JSON) ve referans zamanı."""
import json
import os
import time
from datetime import datetime, timedelta

from core.paths import DATA_DIR

DATA_FILE = os.path.join(DATA_DIR, "veriler.json")


def default_settings() -> dict:
    return {
        "time_offset_seconds": 0,
        "life_target_ts": None,
        "mod3_seg1": 0,
        "mod3_seg2": 8,
        "mod3_seg3": 11,
        "mod3_show_seconds": False,
        "pomodoro": {
            "sound_enabled": True,
            "volume": 85,
            "sound_work_end": True,
            "sound_break_end": True,
            "show_notification": True,
            "work_min": 25,
            "short_break_min": 5,
            "long_break_min": 15,
            "active_task_id": None,
        },
        "screen": {
            "red": 100,
            "green": 100,
            "blue_filter": 0,
            "brightness": 100,
            "darkness": 0,
            "gray": False,
            "reading": False,
            "blue_mode": "Her Zaman",
            "blue_start_hour": 20,
            "blue_end_hour": 7,
            "gray_mode": "Her Zaman",
            "gray_start_hour": 22,
            "gray_end_hour": 6,
        },
    }


class DataManager:
    def __init__(self, path: str = DATA_FILE):
        self.file_name = path
        self.data = {
            "keep_notes": [],
            "tasks": [],
            "habits": [],
            "settings": default_settings(),
        }
        self.load()

    # ---- dosya ----
    def load(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        if not os.path.exists(self.file_name):
            return
        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except Exception as e:
            print(f"Veri okunurken hata: {e}")
            return

        for key in ("keep_notes", "tasks", "habits"):
            if isinstance(loaded.get(key), list):
                self.data[key] = loaded[key]

        for k, v in (loaded.get("settings") or {}).items():
            current = self.data["settings"].get(k)
            if isinstance(v, dict) and isinstance(current, dict):
                current.update(v)
            else:
                self.data["settings"][k] = v

    def save(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        try:
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Veri kaydedilirken hata: {e}")

    # ---- Notlar ----
    def add_keep_note(self, title, text, date_str=None):
        if not date_str:
            date_str = get_now().strftime("%Y-%m-%d %H:%M")
        note = {
            "id": str(time.time()),
            "title": title.strip(),
            "text": text.strip(),
            "date": date_str,
        }
        self.data["keep_notes"].insert(0, note)
        self.save()
        return note

    def delete_keep_note(self, note_id):
        self.data["keep_notes"] = [n for n in self.data["keep_notes"] if n["id"] != note_id]
        self.save()

    def update_keep_note(self, note_id, title, text):
        for n in self.data["keep_notes"]:
            if n["id"] == note_id:
                n["title"] = title.strip()
                n["text"] = text.strip()
                break
        self.save()

    # ---- Görevler ----
    def add_task(self, title, priority="Orta", task_date="", task_time=""):
        task = {
            "id": str(time.time()),
            "title": title.strip(),
            "priority": priority,
            "date": task_date,
            "time": task_time,
            "completed": False,
            "pomodoro_sessions": 0,
        }
        self.data["tasks"].append(task)
        self.save()
        return task

    def toggle_task(self, task_id):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t["completed"] = not t["completed"]
                break
        self.save()

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        self.save()

    def increment_task_pomo(self, task_id):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t["pomodoro_sessions"] += 1
                break
        self.save()

    # ---- Alışkanlıklar ----
    def add_habit(self, name):
        habit = {
            "id": str(time.time()),
            "name": name.strip(),
            "start_date": get_now().date().isoformat(),
            "failed": [],
        }
        self.data["habits"].append(habit)
        self.save()
        return habit

    def delete_habit(self, habit_id):
        self.data["habits"] = [h for h in self.data["habits"] if h["id"] != habit_id]
        self.save()

    def toggle_failed(self, habit_id, day_index):
        for h in self.data["habits"]:
            if h["id"] == habit_id:
                if day_index in h["failed"]:
                    h["failed"].remove(day_index)
                else:
                    h["failed"].append(day_index)
                break
        self.save()


db = DataManager()


def get_now() -> datetime:
    """Referans saatine göre şimdiki zaman (Ayarlar > Tarih ile değiştirilebilir)."""
    offset = db.data["settings"].get("time_offset_seconds", 0) or 0
    return datetime.now() + timedelta(seconds=offset)
