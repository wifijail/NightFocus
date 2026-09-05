"""Global hotkey registration that degrades gracefully instead of crashing.

On Linux, the ``keyboard`` package usually needs root or a udev rule to
read raw input devices. On locked-down systems it may also be blocked
entirely. Either way, Night Focus should keep working -- just without
the global shortcut -- so every failure here is caught and reported as
a boolean rather than an exception.
"""

import logging

logger = logging.getLogger(__name__)

try:
    import keyboard

    _KEYBOARD_AVAILABLE = True
except ImportError:
    keyboard = None
    _KEYBOARD_AVAILABLE = False


class HotkeyService:
    def __init__(self, combo: str, callback):
        self.combo = combo
        self.callback = callback
        self.active = False

    def register(self) -> bool:
        if not _KEYBOARD_AVAILABLE:
            logger.warning("The 'keyboard' package is not available; global hotkey disabled.")
            return False
        try:
            keyboard.add_hotkey(self.combo, self.callback)
            self.active = True
            return True
        except Exception as exc:
            logger.warning("Could not register global hotkey %s: %s", self.combo, exc)
            self.active = False
            return False

    def unregister(self) -> None:
        if self.active and _KEYBOARD_AVAILABLE:
            try:
                keyboard.remove_hotkey(self.combo)
            except Exception:
                pass
        self.active = False
