"""System tray icon: menu, tooltip, and double-click to reopen."""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMenu, QStyle, QSystemTrayIcon


class TrayIcon(QObject):
    open_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent_widget, strings: dict):
        super().__init__(parent_widget)

        self.tray = QSystemTrayIcon(parent_widget)
        self.tray.setIcon(parent_widget.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

        self.menu = QMenu()
        self.show_action = self.menu.addAction("")
        self.quit_action = self.menu.addAction("")
        self.show_action.triggered.connect(self.open_requested.emit)
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self.tray.setContextMenu(self.menu)

        self.tray.activated.connect(self._on_activated)
        self.retranslate(strings)
        self.tray.show()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_requested.emit()

    def retranslate(self, strings: dict) -> None:
        self.show_action.setText(strings["tray_show"])
        self.quit_action.setText(strings["tray_quit"])
        self.tray.setToolTip(strings["app_title"])

    def notify(self, title: str, message: str) -> None:
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
