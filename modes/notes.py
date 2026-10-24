"""Mod 2: Notlar."""
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
)

from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase


class NoteDialog(QDialog):
    def __init__(self, title="", text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Not Düzenle")
        self.setMinimumSize(420, 320)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Başlık:"))
        self.title_in = QLineEdit(title)
        layout.addWidget(self.title_in)
        layout.addWidget(QLabel("Not Metni:"))
        self.text_in = QTextEdit()
        self.text_in.setPlainText(text)
        layout.addWidget(self.text_in)

        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Save).setText("Kaydet")
        btn_box.button(QDialogButtonBox.Cancel).setText("İptal")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_data(self):
        return self.title_in.text(), self.text_in.toPlainText()


class Mode(ModeBase):
    TITLE = "Notlar"

    def build_ui(self):
        layout = QVBoxLayout(self)

        top_bar = QFrame()
        top_layout = QHBoxLayout(top_bar)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Notlarda ara...")
        self.search_input.textChanged.connect(self.refresh_notes)
        top_layout.addWidget(self.search_input, 3)

        self.add_btn = ModernButton("+ Yeni Not Ekle", tooltip="Yeni Not Oluştur", role="success")
        self.add_btn.clicked.connect(self.open_add_dialog)
        top_layout.addWidget(self.add_btn, 1)
        layout.addWidget(top_bar)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("QListWidget::item { margin: 4px; border-radius: 8px; }")
        self.list_widget.itemDoubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.list_widget)

        self.ctx.add_notes_listener(self.refresh_notes)
        self.refresh_notes()

    def open_add_dialog(self):
        dlg = NoteDialog("", "", self)
        if dlg.exec_() == QDialog.Accepted:
            t, txt = dlg.get_data()
            if t or txt:
                self.ctx.db.add_keep_note(t if t else "Başlıksız Not", txt)
                self.ctx.notes_changed()

    def open_edit_dialog(self, item):
        note_id = item.data(Qt.UserRole)
        note = next((n for n in self.ctx.db.data["keep_notes"] if n["id"] == note_id), None)
        if not note:
            return
        dlg = NoteDialog(note["title"], note["text"], self)
        if dlg.exec_() == QDialog.Accepted:
            t, txt = dlg.get_data()
            self.ctx.db.update_keep_note(note_id, t, txt)
            self.ctx.notes_changed()

    def delete_note(self, note_id):
        self.ctx.db.delete_keep_note(note_id)
        self.ctx.notes_changed()

    def refresh_notes(self):
        self.list_widget.clear()
        query = self.search_input.text().lower()
        colors = [C.PANEL, C.PANEL_ALT]

        for idx, note in enumerate(self.ctx.db.data["keep_notes"]):
            if query and query not in note["title"].lower() and query not in note["text"].lower():
                continue

            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background-color: {colors[idx % 2]}; border: 1px solid {C.BORDER};"
                f" border-radius: 8px; padding: 8px; }}"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(6)
            card_layout.setContentsMargins(10, 8, 10, 8)

            header = QHBoxLayout()
            title_lbl = QLabel(f"[Not] {note['title']}")
            title_lbl.setStyleSheet(f"font-weight: bold; color: {C.HEADING}; border: none;")
            f = QFont(); f.setPointSize(11)
            title_lbl.setFont(f)
            header.addWidget(title_lbl, 1)

            date_lbl = QLabel(note["date"])
            date_lbl.setStyleSheet(f"color: {C.TEXT_MUTED}; border: none;")
            header.addWidget(date_lbl)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(26, 26)
            del_btn.setToolTip("Notu Sil")
            del_btn.setStyleSheet(f"background: transparent; color: {C.DANGER}; font-weight: bold; border: none;")
            del_btn.clicked.connect(lambda _, nid=note["id"]: self.delete_note(nid))
            header.addWidget(del_btn)
            card_layout.addLayout(header)

            text_lbl = QLabel(note["text"] if note["text"] else "(Boş not)")
            text_lbl.setWordWrap(True)
            text_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            text_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
            text_lbl.setStyleSheet(f"color: {C.TEXT_SOFT}; border: none;")
            card_layout.addWidget(text_lbl)

            card.adjustSize()
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.list_widget.width() - 20, max(80, card.sizeHint().height() + 12)))
            item.setData(Qt.UserRole, note["id"])
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)
