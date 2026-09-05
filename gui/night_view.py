"""Night mode: capture text, a screenshot, a voice note, and tags."""

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.audio_service import AudioRecorderService, AudioServiceError
from services.screenshot_service import ScreenshotError, ScreenshotService


class NightView(QWidget):
    save_requested = pyqtSignal(dict)
    mic_unavailable = pyqtSignal()

    def __init__(self, audio_file: Path, screenshot_file: Path, sample_rate: int, parent=None):
        super().__init__(parent)
        self.audio_file = audio_file
        self.screenshot_file = screenshot_file
        self.audio_service = AudioRecorderService(sample_rate=sample_rate)
        self.screenshot_service = ScreenshotService()

        self.attached_screenshot: str | None = None
        self.attached_audio: str | None = None
        self._strings: dict = {}

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.hide()
        layout.addWidget(self.lbl_preview)

        media_bar = QHBoxLayout()
        self.btn_screenshot = QPushButton()
        self.btn_screenshot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_screenshot.clicked.connect(self._take_screenshot)
        media_bar.addWidget(self.btn_screenshot)

        self.btn_record = QPushButton()
        self.btn_record.setObjectName("RecordBtn")
        self.btn_record.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_record.clicked.connect(self._toggle_recording)
        media_bar.addWidget(self.btn_record)
        layout.addLayout(media_bar)

        status_bar = QHBoxLayout()
        self.lbl_shot_status = QLabel("")
        status_bar.addWidget(self.lbl_shot_status)
        self.lbl_audio_status = QLabel("")
        status_bar.addWidget(self.lbl_audio_status)
        status_bar.addStretch()
        layout.addLayout(status_bar)

        self.tag_input = QLineEdit()
        layout.addWidget(self.tag_input)

        self.btn_save = QPushButton()
        self.btn_save.setObjectName("PrimaryBtn")
        self.btn_save.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setMinimumHeight(45)
        self.btn_save.clicked.connect(self._save)
        layout.addWidget(self.btn_save)

        self.lbl_hint = QLabel("")
        self.lbl_hint.setObjectName("HintLabel")
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_hint)

    def retranslate(self, strings: dict) -> None:
        self._strings = strings
        self.text_edit.setPlaceholderText(strings["placeholder_text"])
        self.btn_screenshot.setText(strings["btn_shot"])
        self.btn_record.setText(strings["btn_stop"] if self.audio_service.is_recording else strings["btn_rec"])
        self.tag_input.setPlaceholderText(strings["placeholder_tags"])
        self.btn_save.setText(strings["btn_save"])
        if self.attached_screenshot:
            self.lbl_shot_status.setText(strings["shot_ok"])
        if self.attached_audio:
            self.lbl_audio_status.setText(strings["audio_ok"])

    @staticmethod
    def _repolish(widget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _set_status(self, label: QLabel, text: str, status: str) -> None:
        label.setText(text)
        label.setProperty("status", status)
        self._repolish(label)

    def show_status(self, message: str, duration_ms: int = 2000) -> None:
        self.lbl_hint.setText(message)
        QTimer.singleShot(duration_ms, lambda: self.lbl_hint.setText(""))

    def _take_screenshot(self) -> None:
        window = self.window()
        window.hide()
        QTimer.singleShot(400, self._grab_screen)

    def _grab_screen(self) -> None:
        try:
            path = self.screenshot_service.capture(self.screenshot_file)
            self.attached_screenshot = path
            self._set_status(self.lbl_shot_status, self._strings["shot_ok"], "ok")

            pixmap = QPixmap(path)
            scaled = pixmap.scaled(
                200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_preview.setPixmap(scaled)
            self.lbl_preview.show()
        except ScreenshotError:
            self._set_status(self.lbl_shot_status, self._strings["shot_err"], "err")
        self.window().show()

    def _toggle_recording(self) -> None:
        strings = self._strings
        if not self.audio_service.is_recording:
            try:
                self.audio_service.start()
            except AudioServiceError:
                self.mic_unavailable.emit()
                return
            self.btn_record.setProperty("recording", "true")
            self._repolish(self.btn_record)
            self.btn_record.setText(strings["btn_stop"])
        else:
            saved = self.audio_service.stop(self.audio_file)
            self.btn_record.setProperty("recording", "false")
            self._repolish(self.btn_record)
            self.btn_record.setText(strings["btn_rec"])
            if saved:
                self.attached_audio = str(self.audio_file)
                self._set_status(self.lbl_audio_status, strings["audio_ok"], "ok")

    def _save(self) -> None:
        data = {
            "text": self.text_edit.toPlainText().strip(),
            "tags": self.tag_input.text().strip(),
            "screenshot": self.attached_screenshot,
            "audio": self.attached_audio,
        }
        if not any(data.values()):
            self.show_status(self._strings.get("nothing_to_save", ""))
            return
        self.save_requested.emit(data)

    def reset(self) -> None:
        self.text_edit.clear()
        self.tag_input.clear()
        self.lbl_preview.hide()
        self.lbl_shot_status.setText("")
        self.lbl_audio_status.setText("")
        self.attached_screenshot = None
        self.attached_audio = None
