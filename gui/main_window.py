"""Top-level window: header chrome, mode switching, and service wiring."""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import config
from gui import styles
from gui.animations import fade_in, fade_out
from gui.morning_view import MorningView
from gui.night_view import NightView
from gui.tray import TrayIcon
from locales import AVAILABLE_LANGUAGES, get_strings, language_label
from services.autostart_service import AutostartError, AutostartService
from services.hotkey_service import HotkeyService
from services.storage_service import SessionStorage, SettingsStorage


class MainWindow(QWidget):
    hotkey_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.settings_storage = SettingsStorage(config.SETTINGS_FILE, config.DEFAULT_SETTINGS)
        self.settings = self.settings_storage.load()
        self.session_storage = SessionStorage(config.DATA_FILE)
        self.autostart_service = AutostartService(config.APP_NAME)
        self.mode = "night"
        self._drag_position = None

        self._init_window()
        self._build_ui()
        self._connect_views()

        self.tray = TrayIcon(self, self.strings)
        self.tray.open_requested.connect(self.wake_up)
        self.tray.quit_requested.connect(QApplication.quit)

        self.hotkey_signal.connect(self.wake_up)
        self.hotkey_service = HotkeyService(self.settings["hotkey"], self.hotkey_signal.emit)
        if not self.hotkey_service.register():
            self._notify_hotkey_failed()

        self._maybe_ask_autostart()
        self.refresh_mode()

    @property
    def strings(self) -> dict:
        return get_strings(self.settings["language"])

    # -- construction -----------------------------------------------------

    def _init_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(*config.WINDOW_MIN_SIZE)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(15, 15, 15, 15)

        self.container = QFrame()
        self.container.setObjectName("MainFrame")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)
        outer.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(16)

        header = QHBoxLayout()
        self.header_label = QLabel()
        self.header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(self.header_label)
        header.addStretch()

        self.language_combo = QComboBox()
        for code, _label in AVAILABLE_LANGUAGES:
            self.language_combo.addItem(language_label(code), userData=code)
        self.language_combo.setCurrentIndex(self._language_index())
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        header.addWidget(self.language_combo)

        self.btn_theme = QPushButton("🌗")
        self.btn_theme.setObjectName("IconBtn")
        self.btn_theme.setFixedSize(30, 30)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self._toggle_theme)
        header.addWidget(self.btn_theme)

        self.btn_close = QPushButton("✖")
        self.btn_close.setObjectName("CloseBtn")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)

        container_layout.addLayout(header)

        self.night_view = NightView(config.AUDIO_FILE, config.SHOT_FILE, config.SAMPLE_RATE)
        self.morning_view = MorningView()
        container_layout.addWidget(self.night_view)
        container_layout.addWidget(self.morning_view)

        self._apply_theme()

    def _connect_views(self) -> None:
        self.night_view.save_requested.connect(self._on_save)
        self.night_view.mic_unavailable.connect(self._on_mic_unavailable)
        self.morning_view.completed.connect(self._on_completed)

    def _language_index(self) -> int:
        codes = [code for code, _ in AVAILABLE_LANGUAGES]
        return codes.index(self.settings["language"]) if self.settings["language"] in codes else 0

    # -- theming & language -------------------------------------------------

    def _apply_theme(self) -> None:
        self.container.setStyleSheet(styles.get_stylesheet(self.settings["theme"]))

    def _toggle_theme(self) -> None:
        self.settings["theme"] = "light" if self.settings["theme"] == "dark" else "dark"
        self._apply_theme()
        self.settings_storage.save(self.settings)

    def _on_language_changed(self, index: int) -> None:
        code = self.language_combo.itemData(index)
        if code == self.settings["language"]:
            return
        self.settings["language"] = code
        self.settings_storage.save(self.settings)
        self.retranslate()

    def retranslate(self) -> None:
        strings = self.strings
        self.header_label.setText(strings["header_night"] if self.mode == "night" else strings["header_morning"])
        self.btn_theme.setToolTip(strings["theme_tooltip"])
        self.language_combo.setToolTip(strings["language_tooltip"])
        self.night_view.retranslate(strings)
        self.morning_view.retranslate(strings)
        self.tray.retranslate(strings)

    # -- mode switching -----------------------------------------------------

    def refresh_mode(self) -> None:
        self.mode = "morning" if self.session_storage.exists() else "night"
        if self.mode == "morning":
            data = self.session_storage.load() or {}
            self.morning_view.load_data(data, self.strings)
            self.morning_view.show()
            self.night_view.hide()
        else:
            self.night_view.show()
            self.morning_view.hide()
        self.retranslate()

    def _on_save(self, data: dict) -> None:
        self.session_storage.save(data)
        self.night_view.reset()
        self.close()

    def _on_completed(self) -> None:
        self.morning_view.stop_playback()
        self.session_storage.clear()
        Path(config.AUDIO_FILE).unlink(missing_ok=True)
        Path(config.SHOT_FILE).unlink(missing_ok=True)
        self.close()

    # -- error handling -----------------------------------------------------

    def _on_mic_unavailable(self) -> None:
        strings = self.strings
        QMessageBox.warning(self, strings["mic_missing_title"], strings["mic_missing_msg"])

    def _notify_hotkey_failed(self) -> None:
        strings = self.strings
        self.tray.notify(strings["hotkey_failed_title"], strings["hotkey_failed_msg"])

    def _maybe_ask_autostart(self) -> None:
        if self.autostart_service.is_enabled():
            return
        strings = self.strings
        box = QMessageBox(self)
        box.setWindowTitle(strings["autostart_title"])
        box.setText(strings["autostart_msg"])
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setStyleSheet(styles.get_stylesheet(self.settings["theme"]))
        if box.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.autostart_service.enable()
            except AutostartError:
                QMessageBox.warning(self, strings["autostart_error_title"], strings["autostart_error_msg"])

    # -- window lifecycle -----------------------------------------------------

    def wake_up(self) -> None:
        self.refresh_mode()
        self.show()
        fade_in(self, config.FADE_IN_MS)
        self.activateWindow()

    def closeEvent(self, event) -> None:
        event.ignore()

        def _finish_hide():
            self.hide()
            self.tray.notify(config.APP_NAME, self.strings["tray_msg"])

        fade_out(self, config.FADE_OUT_MS, on_finished=_finish_hide)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
