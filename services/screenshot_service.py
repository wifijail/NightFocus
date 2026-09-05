"""Full-screen capture, isolated so display/permission errors don't crash the UI."""

from pathlib import Path

from PIL import ImageGrab


class ScreenshotError(Exception):
    """Raised when a screenshot could not be captured or saved."""


class ScreenshotService:
    def capture(self, output_path: Path) -> str:
        try:
            image = ImageGrab.grab()
            image.save(str(output_path))
        except Exception as exc:
            raise ScreenshotError(str(exc)) from exc
        return str(output_path)
