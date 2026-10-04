"""Stages 3 and 4 - frame difference, threshold, motion score and centroid."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class MotionResult:
    score: int                                   # number of changed pixels
    centroid: Optional[Tuple[float, float]]      # (x, y) center of the changed area
    mask: Optional[np.ndarray]                   # black and white motion mask


class MotionDetector:
    def __init__(self, pixel_cutoff: int = 25):
        self._cutoff = pixel_cutoff
        self._prev: Optional[np.ndarray] = None

    def analyse(self, gray: np.ndarray) -> MotionResult:
        if self._prev is None:                   # first frame: nothing to compare with yet
            self._prev = gray
            return MotionResult(0, None, None)

        diff = cv2.absdiff(self._prev, gray)
        mask = cv2.threshold(diff, self._cutoff, 255, cv2.THRESH_BINARY)[1]
        self._prev = gray

        score = cv2.countNonZero(mask)
        centroid = None
        if score > 0:
            m = cv2.moments(mask, binaryImage=True)
            if m["m00"] > 0:
                centroid = (m["m10"] / m["m00"], m["m01"] / m["m00"])
        return MotionResult(score, centroid, mask)
