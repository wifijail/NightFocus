"""Application-wide configuration: storage locations and defaults."""

import os
import sys
from pathlib import Path

APP_NAME = "NightFocus"


def _app_data_dir() -> Path:
    """Return the per-user application data directory for the current OS."""
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        path = Path(base) / APP_NAME
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        path = Path(base) / APP_NAME.lower()

    path.mkdir(parents=True, exist_ok=True)
    return path


APP_DATA_DIR = _app_data_dir()

DATA_FILE = APP_DATA_DIR / "session.json"
AUDIO_FILE = APP_DATA_DIR / "voice_note.wav"
SHOT_FILE = APP_DATA_DIR / "screenshot.png"
SETTINGS_FILE = APP_DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "dark",
    "hotkey": "ctrl+alt+n",
}

SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1

WINDOW_MIN_SIZE = (600, 700)
FADE_IN_MS = 220
FADE_OUT_MS = 180
