"""The whole architecture in one testable class: frame in, FrameResult out."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .config import Config
from .detector import MotionDetector
from .direction import DirectionTracker
from .preprocess import preprocess
from .state import MotionState


@dataclass(frozen=True)
class FrameResult:
    moving: bool
    direction: Optional[str]
    score: int
    mask: Optional[np.ndarray] = None

    @property
    def label(self) -> str:
        if not self.moving:
            return "Body in rest"
        if self.direction:
            return f"Motion detected - {self.direction}"
        return "Motion detected"


class MotionPipeline:
    def __init__(self, config: Config):
        self._cfg = config
        self._detector = MotionDetector(config.pixel_cutoff)
        self._state = MotionState(config.motion_threshold, config.rest_delay_frames)
        self._tracker = DirectionTracker(config.history_length, config.min_shift)

    def process(self, frame: np.ndarray) -> FrameResult:
        gray = preprocess(frame, self._cfg.blur_kernel)           # stage 2
        result = self._detector.analyse(gray)                     # stages 3-4, 6
        moving = self._state.update(result.score)                 # stage 5

        direction = None
        if self._state.is_active(result.score) and result.centroid is not None:
            direction = self._tracker.update(result.centroid)     # stages 7-8
        if not moving:
            self._tracker.reset()
        return FrameResult(moving, direction, result.score, result.mask)
