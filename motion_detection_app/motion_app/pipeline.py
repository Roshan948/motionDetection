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
    score: float                       # percent of the frame that changed
    mask: Optional[np.ndarray] = None  # only filled when process(keep_mask=True)

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
        self._state = MotionState(config.motion_threshold_ratio, config.rest_delay_frames)
        self._tracker = DirectionTracker(config.history_length, config.min_shift)
        self._inactive_frames = 0

    def process(self, frame: np.ndarray, keep_mask: bool = False) -> FrameResult:
        gray = preprocess(frame, self._cfg.blur_kernel, self._cfg.process_width)   # stage 2
        result = self._detector.analyse(gray, keep_mask)                           # stages 3-4, 6
        active = self._state.is_active(result.ratio)
        moving = self._state.update(result.ratio)                                  # stage 5

        # Forget old centroids after a pause, so a new movement is never compared with
        # positions from before it. This does not wait for the (slower) rest delay.
        self._inactive_frames = 0 if active else self._inactive_frames + 1
        if not moving or self._inactive_frames > self._cfg.direction_reset_frames:
            self._tracker.reset()

        direction = None
        if active and result.centroid is not None:
            direction = self._tracker.update(result.centroid)                      # stages 7-8
        return FrameResult(moving, direction, result.ratio * 100, result.mask)
