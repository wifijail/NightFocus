"""Theme palettes and the QSS stylesheet built from them."""

DARK = {
    "bg": "#121214",
    "border": "#27272A",
    "surface": "#18181B",
    "surface_border": "#27272A",
    "text": "#F4F4F5",
    "text_bright": "#FAFAFA",
    "muted": "#A1A1AA",
    "accent": "#6366F1",
    "accent_hover": "#4F46E5",
    "danger": "#EF4444",
    "success": "#10B981",
    "button_bg": "#27272A",
    "button_hover": "#3F3F46",
    "button_border": "#3F3F46",
}

LIGHT = {
    "bg": "#FAFAFA",
    "border": "#E4E4E7",
    "surface": "#FFFFFF",
    "surface_border": "#E4E4E7",
    "text": "#18181B",
    "text_bright": "#09090B",
    "muted": "#71717A",
    "accent": "#6366F1",
    "accent_hover": "#4F46E5",
    "danger": "#DC2626",
    "success": "#059669",
    "button_bg": "#F4F4F5",
    "button_hover": "#E4E4E7",
    "button_border": "#D4D4D8",
}


def _build(palette: dict) -> str:
    return f"""
QWidget#MainFrame {{ background-color: {palette['bg']}; border: 1px solid {palette['border']}; border-radius: 16px; }}
QLabel {{ color: {palette['text']}; font-family: 'Segoe UI', sans-serif; }}
QTextEdit, QLineEdit {{ background-color: {palette['surface']}; border: 1px solid {palette['surface_border']}; border-radius: 10px; color: {palette['text_bright']}; padding: 10px; font-size: 14px; }}
QTextEdit:focus, QLineEdit:focus {{ border: 1px solid {palette['accent']}; }}
QComboBox {{ background-color: {palette['button_bg']}; border: 1px solid {palette['button_border']}; border-radius: 8px; color: {palette['text']}; padding: 4px 10px; }}
QComboBox QAbstractItemView {{ background-color: {palette['surface']}; color: {palette['text']}; selection-background-color: {palette['accent']}; selection-color: #FFFFFF; }}
QPushButton {{ background-color: {palette['button_bg']}; border: 1px solid {palette['button_border']}; border-radius: 10px; color: {palette['text_bright']}; font-weight: 600; padding: 8px 16px; font-size: 13px; }}
QPushButton:hover {{ background-color: {palette['button_hover']}; }}
QPushButton#PrimaryBtn {{ background-color: {palette['accent']}; border: none; color: #FFFFFF; }}
QPushButton#PrimaryBtn:hover {{ background-color: {palette['accent_hover']}; }}
QPushButton#RecordBtn[recording="true"] {{ background-color: {palette['danger']}; color: white; }}
QPushButton#IconBtn {{ background-color: transparent; border: none; color: {palette['muted']}; font-size: 14px; padding: 0; font-weight: bold; }}
QPushButton#IconBtn:hover {{ color: {palette['text_bright']}; }}
QPushButton#CloseBtn {{ background-color: transparent; border: none; color: {palette['muted']}; font-size: 16px; padding: 0; }}
QPushButton#CloseBtn:hover {{ color: {palette['danger']}; }}
QFrame#MediaCard {{ background-color: {palette['surface']}; border: 1px solid {palette['surface_border']}; border-radius: 12px; }}
QScrollArea {{ border: none; background: transparent; }}
QLabel[status="ok"] {{ color: {palette['success']}; font-size: 12px; font-weight: 600; }}
QLabel[status="err"] {{ color: {palette['danger']}; font-size: 12px; font-weight: 600; }}
QLabel#AccentLabel {{ color: {palette['accent']}; font-weight: 600; font-size: 13px; }}
QLabel#HintLabel {{ color: {palette['muted']}; font-size: 12px; }}
QMessageBox {{ background-color: {palette['bg']}; color: {palette['text']}; }}
QMessageBox QLabel {{ color: {palette['text']}; }}
"""


def get_stylesheet(theme: str) -> str:
    palette = LIGHT if theme == "light" else DARK
    return _build(palette)
