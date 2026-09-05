"""Small opacity-fade helpers used when showing/hiding the main window."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation


def fade_in(widget, duration: int = 220) -> QPropertyAnimation:
    widget.setWindowOpacity(0.0)
    animation = QPropertyAnimation(widget, b"windowOpacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._fade_animation = animation  # keep a reference alive
    return animation


def fade_out(widget, duration: int = 180, on_finished=None) -> QPropertyAnimation:
    animation = QPropertyAnimation(widget, b"windowOpacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(widget.windowOpacity())
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.Type.InCubic)
    if on_finished is not None:
        animation.finished.connect(on_finished)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._fade_animation = animation  # keep a reference alive
    return animation
