"""Stage 1 - webcam capture."""
from __future__ import annotations

from typing import Optional

import cv2
import numpy as np


class Camera:
    """Thin wrapper around cv2.VideoCapture. Use it as a context manager."""

    def __init__(self, index: int = 0, mirror: bool = True):
        self._index = index
        self._mirror = mirror
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> "Camera":
        cap = cv2.VideoCapture(self._index)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(
                f"Could not open camera {self._index}. "
                "Check that a webcam is connected and not used by another app."
            )
        self._cap = cap
        return self

    def read(self) -> Optional[np.ndarray]:
        """Return the next frame, or None if the camera stopped delivering."""
        if self._cap is None:
            raise RuntimeError("Camera is not open")
        ok, frame = self._cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1) if self._mirror else frame

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> "Camera":
        return self.open()

    def __exit__(self, *exc) -> None:
        self.release()
