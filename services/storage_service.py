"""Reading and writing the JSON files Night Focus persists to disk."""

import json
from pathlib import Path
from typing import Optional


class SessionStorage:
    """Stores the single pending night-capture session, if any."""

    def __init__(self, data_file: Path):
        self.data_file = Path(data_file)

    def exists(self) -> bool:
        return self.data_file.exists()

    def load(self) -> Optional[dict]:
        if not self.exists():
            return None
        try:
            with open(self.data_file, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, data: dict) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        self.data_file.unlink(missing_ok=True)


class SettingsStorage:
    """Stores small user preferences (language, theme, hotkey)."""

    def __init__(self, settings_file: Path, defaults: dict):
        self.settings_file = Path(settings_file)
        self.defaults = defaults

    def load(self) -> dict:
        data = dict(self.defaults)
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as handle:
                    data.update(json.load(handle))
            except (json.JSONDecodeError, OSError):
                pass
        return data

    def save(self, data: dict) -> None:
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
