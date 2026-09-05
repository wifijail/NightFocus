# 🌙 Night Focus

A small, always-on-top desktop companion that fights "night-time context loss": that moment before bed when you finally remember the one thing you meant to write down, or the point where you stopped mid-task and know you'll forget it by morning.

Night Focus works in two phases. At night, capture a quick note, a screenshot, and a voice memo, then go to sleep. In the morning, it opens automatically with everything laid out, ready to review in one glance.

*Читать на русском: [README.ru.md](README.ru.md)*

## Features

- **Two-phase workflow** — capture at night, review in the morning. The app detects which phase it's in on its own.
- **One-click screenshot** of the full screen, attached to the session.
- **Voice notes**, recorded from the microphone and played back with one click.
- **Tags / priority labels** (`#Urgent`, `#Idea`, ...).
- **Global hotkey** (`Ctrl+Alt+N` by default) to summon the window from anywhere.
- **System tray** — closing the window just hides it; the app keeps running quietly.
- **Autostart on login**, supported on Windows, macOS, and Linux.
- **Six languages** out of the box — English, Русский, Español, Deutsch, Français, Português — switchable anytime from the header.
- **Light and dark themes.**
- **Per-user storage** in the standard OS application-data directory, not scattered loose files in your home folder.
- **Graceful degradation** — the app keeps working without a microphone, without permission to register a global hotkey, or without rights to enable autostart. Each of those failures is caught and surfaced as a small message instead of a crash.

## Screenshots

*Add a short demo GIF here (e.g. recorded with ScreenToGif or Kap) showing the night → morning flow: `docs/demo.gif`*

## Installation

### Requirements

- Python 3.10+ (3.12 recommended)
- Windows, macOS, or Linux with a desktop session

### From source

```bash
git clone https://github.com/<your-username>/night-focus.git
cd night-focus
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

> **Linux note:** the global hotkey relies on the `keyboard` package reading raw input devices, which usually needs root or a one-time udev rule. Night Focus runs fine without it — you'll just open it from the tray icon instead of `Ctrl+Alt+N`.

## Building a standalone executable

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "NightFocus" main.py
```

The result lands in `dist/NightFocus/`. `--windowed` hides the console window on Windows; on macOS it produces a `.app` bundle. Add `--icon path/to/icon.ico` (Windows) or `--icon path/to/icon.icns` (macOS) if you have branded artwork.

## Where your data lives

| OS      | Location                                                        |
|---------|-------------------------------------------------------------------|
| Windows | `%LOCALAPPDATA%\NightFocus`                                       |
| macOS   | `~/Library/Application Support/NightFocus`                        |
| Linux   | `$XDG_DATA_HOME/nightfocus` (defaults to `~/.local/share/nightfocus`) |

Preferences (language, theme, hotkey) are stored in `settings.json` in the same folder; the nightly capture lives in `session.json` alongside the screenshot and voice-note files, and is deleted once you mark it done.

## Project structure

```
night_focus/
├── main.py                    # entry point
├── config.py                  # paths, defaults, constants
├── gui/
│   ├── main_window.py         # frameless window, header, mode switching
│   ├── night_view.py          # capture UI
│   ├── morning_view.py        # review UI
│   ├── tray.py                # system tray icon
│   ├── styles.py               # dark/light QSS themes
│   └── animations.py          # fade in/out helpers
├── services/
│   ├── audio_service.py       # microphone recording
│   ├── screenshot_service.py  # screen capture
│   ├── autostart_service.py   # Windows/macOS/Linux autostart
│   ├── hotkey_service.py      # global hotkey with safe fallback
│   └── storage_service.py     # JSON session & settings persistence
├── locales/
│   ├── en.py / ru.py / es.py / de.py / fr.py / pt.py
│   └── __init__.py            # loader with English fallback
├── requirements.txt
└── README.md
```

## Keyboard shortcut

Default global hotkey: `Ctrl+Alt+N`. To change it, edit `"hotkey"` in `settings.json` (any combination understood by the [`keyboard`](https://github.com/boppreh/keyboard) package, e.g. `"ctrl+shift+space"`).

## Roadmap

- Browse a short history of past nights, not just the latest one
- Change the hotkey from the UI instead of editing `settings.json`
- Export a night's notes to Markdown

## Contributing

Issues and pull requests are welcome. Please run `python -m py_compile $(git ls-files '*.py')` (or your linter of choice) before submitting.

## License

MIT — see [LICENSE](LICENSE).
