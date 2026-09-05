"""Voice-note recording, isolated from the UI so it can fail safely."""

from pathlib import Path

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd


class AudioServiceError(Exception):
    """Raised when recording cannot start (no device, permission, ...)."""


class AudioRecorderService:
    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._stream = None
        self._frames: list[np.ndarray] = []

    def has_input_device(self) -> bool:
        try:
            devices = sd.query_devices()
        except Exception:
            return False
        return any(device.get("max_input_channels", 0) > 0 for device in devices)

    def start(self) -> None:
        if not self.has_input_device():
            raise AudioServiceError("No input device is available.")

        self._frames = []
        self.is_recording = True

        def callback(indata, _frames, _time_info, _status):
            if self.is_recording:
                self._frames.append(indata.copy())

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
            )
            self._stream.start()
        except Exception as exc:
            self.is_recording = False
            self._stream = None
            raise AudioServiceError(str(exc)) from exc

    def stop(self, output_path: Path) -> bool:
        """Stop recording and write a WAV file. Returns False if nothing was captured."""
        self.is_recording = False

        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if not self._frames:
            return False

        audio = np.concatenate(self._frames, axis=0)
        audio = np.clip(audio, -1.0, 1.0)
        wav.write(str(output_path), self.sample_rate, (audio * 32767).astype(np.int16))
        self._frames = []
        return True
