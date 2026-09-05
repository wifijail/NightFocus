"""Enable/disable launching the app automatically on login, per OS."""

import os
import platform
import sys
from pathlib import Path


class AutostartError(Exception):
    """Raised when autostart could not be enabled or disabled."""


class AutostartService:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.system = platform.system()

    def is_enabled(self) -> bool:
        try:
            if self.system == "Windows":
                return self._windows_is_enabled()
            if self.system == "Darwin":
                return self._plist_path().exists()
            return self._desktop_entry_path().exists()
        except Exception:
            return False

    def enable(self) -> None:
        try:
            if self.system == "Windows":
                self._windows_set(enable=True)
            elif self.system == "Darwin":
                self._write_plist()
            else:
                self._write_desktop_entry()
        except (OSError, PermissionError, ImportError) as exc:
            raise AutostartError(str(exc)) from exc

    def disable(self) -> None:
        try:
            if self.system == "Windows":
                self._windows_set(enable=False)
            elif self.system == "Darwin":
                self._plist_path().unlink(missing_ok=True)
            else:
                self._desktop_entry_path().unlink(missing_ok=True)
        except (OSError, PermissionError, ImportError) as exc:
            raise AutostartError(str(exc)) from exc

    # -- Windows --------------------------------------------------------

    def _run_key_path(self) -> str:
        return r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _windows_is_enabled(self) -> bool:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._run_key_path(), 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, self.app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)

    def _windows_set(self, enable: bool) -> None:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._run_key_path(), 0, winreg.KEY_SET_VALUE)
        try:
            if enable:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self._launch_command())
            else:
                try:
                    winreg.DeleteValue(key, self.app_name)
                except FileNotFoundError:
                    pass
        finally:
            winreg.CloseKey(key)

    # -- macOS ------------------------------------------------------------

    def _plist_path(self) -> Path:
        return Path.home() / "Library" / "LaunchAgents" / f"com.{self.app_name.lower()}.plist"

    def _write_plist(self) -> None:
        path = self._plist_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        args_xml = "\n".join(f"        <string>{arg}</string>" for arg in self._launch_args())
        path.write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{self.app_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""",
            encoding="utf-8",
        )

    # -- Linux (XDG autostart) --------------------------------------------

    def _desktop_entry_path(self) -> Path:
        base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(base) / "autostart" / f"{self.app_name.lower()}.desktop"

    def _write_desktop_entry(self) -> None:
        path = self._desktop_entry_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        exec_line = " ".join(self._launch_args())
        path.write_text(
            f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Exec={exec_line}
X-GNOME-Autostart-enabled=true
""",
            encoding="utf-8",
        )

    # -- Shared -------------------------------------------------------------

    def _launch_args(self) -> list[str]:
        if getattr(sys, "frozen", False):
            return [sys.executable]
        return [sys.executable, os.path.abspath(sys.argv[0])]

    def _launch_command(self) -> str:
        return " ".join(f'"{arg}"' for arg in self._launch_args())
