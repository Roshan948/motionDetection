"""Stage 1 - webcam capture."""
from __future__ import annotations

import time
from typing import Optional

import cv2
import numpy as np


class CameraError(RuntimeError):
    """The camera could not be opened, or stopped delivering frames."""


class Camera:
    """Thin wrapper around cv2.VideoCapture. Use it as a context manager."""

    def __init__(self, index: int = 0, mirror: bool = True,
                 retries: int = 5, retry_delay: float = 0.2):
        self._index = index
        self._mirror = mirror
        self._retries = retries
        self._retry_delay = retry_delay
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> "Camera":
        cap = cv2.VideoCapture(self._index)
        if not cap.isOpened():
            cap.release()
            raise CameraError(
                f"Could not open camera {self._index}. "
                "Check that a webcam is connected and not used by another app."
            )
        self._cap = cap
        return self

    def read(self) -> np.ndarray:
        """Return the next frame.

        A failed read is retried a few times, because webcams sometimes drop a frame
        for a moment. If it keeps failing, CameraError explains what happened.
        """
        if self._cap is None:
            raise CameraError("Camera is not open")
        for attempt in range(self._retries + 1):
            ok, frame = self._cap.read()
            if ok:
                return cv2.flip(frame, 1) if self._mirror else frame
            if attempt < self._retries:
                time.sleep(self._retry_delay)
        raise CameraError(
            f"Camera {self._index} stopped delivering frames "
            f"(still failing after {self._retries} retries). "
            "Check the connection and that no other app is using it."
        )

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> "Camera":
        return self.open()

    def __exit__(self, *exc) -> None:
        self.release()
