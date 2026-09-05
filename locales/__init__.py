"""Translation loader.

Every language module exposes a ``STRINGS`` dict. Missing keys in a
non-English module fall back to the English value, so a partial
translation never breaks the UI.
"""

from importlib import import_module

AVAILABLE_LANGUAGES = [
    ("en", "English"),
    ("ru", "Русский"),
    ("es", "Español"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("pt", "Português"),
]

_cache: dict[str, dict[str, str]] = {}


def get_strings(lang_code: str) -> dict:
    if lang_code in _cache:
        return _cache[lang_code]

    base = import_module("locales.en").STRINGS
    if lang_code == "en":
        merged = dict(base)
    else:
        try:
            overrides = import_module(f"locales.{lang_code}").STRINGS
            merged = {**base, **overrides}
        except ModuleNotFoundError:
            merged = dict(base)

    _cache[lang_code] = merged
    return merged


def language_label(code: str) -> str:
    for candidate, label in AVAILABLE_LANGUAGES:
        if candidate == code:
            return label
    return code.upper()
