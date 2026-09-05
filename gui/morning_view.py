"""Morning mode: review whatever was captured the night before."""

from pathlib import Path

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class MorningView(QWidget):
    completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.playbackStateChanged.connect(self._on_playback_state_changed)

        self._data: dict = {}
        self._strings: dict = {}
        self.lbl_tags_val: QLabel | None = None
        self.lbl_audio_title: QLabel | None = None
        self.btn_play: QPushButton | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(14)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        self.btn_complete = QPushButton()
        self.btn_complete.setObjectName("PrimaryBtn")
        self.btn_complete.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_complete.setMinimumHeight(45)
        self.btn_complete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_complete.clicked.connect(self.completed.emit)
        layout.addWidget(self.btn_complete)

    def load_data(self, data: dict, strings: dict) -> None:
        self._data = data
        self._rebuild_cards()
        self.retranslate(strings)

    def _clear_cards(self) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.lbl_tags_val = None
        self.lbl_audio_title = None
        self.btn_play = None

    def _rebuild_cards(self) -> None:
        self._clear_cards()
        data = self._data

        if data.get("text"):
            card = QFrame()
            card.setObjectName("MediaCard")
            card_layout = QVBoxLayout(card)
            label = QLabel(data["text"])
            label.setWordWrap(True)
            label.setFont(QFont("Segoe UI", 12))
            card_layout.addWidget(label)
            self.scroll_layout.addWidget(card)

        if data.get("tags"):
            self.lbl_tags_val = QLabel()
            self.lbl_tags_val.setObjectName("AccentLabel")
            self.scroll_layout.addWidget(self.lbl_tags_val)

        audio_path = data.get("audio")
        if audio_path and Path(audio_path).exists():
            card = QFrame()
            card.setObjectName("MediaCard")
            card_layout = QHBoxLayout(card)
            self.lbl_audio_title = QLabel()
            self.lbl_audio_title.setFont(QFont("Segoe UI", 11))
            self.btn_play = QPushButton()
            self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_play.clicked.connect(lambda: self._toggle_play(audio_path))
            card_layout.addWidget(self.lbl_audio_title)
            card_layout.addWidget(self.btn_play)
            self.scroll_layout.addWidget(card)

        screenshot_path = data.get("screenshot")
        if screenshot_path and Path(screenshot_path).exists():
            card = QFrame()
            card.setObjectName("MediaCard")
            card_layout = QVBoxLayout(card)
            pixmap = QPixmap(screenshot_path)
            scaled = pixmap.scaled(
                500, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            image_label = QLabel()
            image_label.setPixmap(scaled)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(image_label)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _toggle_play(self, audio_path: str) -> None:
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.setSource(QUrl.fromLocalFile(audio_path))
            self.media_player.play()

    def _on_playback_state_changed(self, _state) -> None:
        if self.btn_play is not None:
            self.retranslate(self._strings)

    def retranslate(self, strings: dict) -> None:
        self._strings = strings
        self.btn_complete.setText(strings["btn_done"])
        if self.lbl_tags_val is not None:
            self.lbl_tags_val.setText(f"{strings['lbl_tags']} {self._data.get('tags', '')}")
        if self.lbl_audio_title is not None:
            self.lbl_audio_title.setText(strings["lbl_audio"])
        if self.btn_play is not None:
            playing = self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            self.btn_play.setText(strings["btn_playing"] if playing else strings["btn_play"])

    def stop_playback(self) -> None:
        self.media_player.stop()
