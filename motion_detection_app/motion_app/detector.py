"""Stages 3 and 4 - frame difference, threshold, motion score and centroid."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class MotionResult:
    changed_pixels: int                          # number of changed pixels
    ratio: float                                 # changed_pixels / frame area (0.0 to 1.0)
    centroid: Optional[Tuple[float, float]]      # (x, y) center of the changed area
    mask: Optional[np.ndarray]                   # black and white motion mask, if requested


class MotionDetector:
    def __init__(self, pixel_cutoff: int = 25):
        self._cutoff = pixel_cutoff
        self._prev: Optional[np.ndarray] = None

    def analyse(self, gray: np.ndarray, keep_mask: bool = False) -> MotionResult:
        """Compare this frame with the previous one.

        The mask is needed internally to count pixels and find the centroid, so it cannot
        be skipped; keep_mask only controls whether it is handed back to the caller.
        """
        if self._prev is None or self._prev.shape != gray.shape:
            self._prev = gray            # first frame (or resolution changed): nothing to compare
            return MotionResult(0, 0.0, None, None)

        diff = cv2.absdiff(self._prev, gray)
        mask = cv2.threshold(diff, self._cutoff, 255, cv2.THRESH_BINARY)[1]
        self._prev = gray

        changed = cv2.countNonZero(mask)
        ratio = changed / mask.size
        centroid = None
        if changed > 0:
            m = cv2.moments(mask, binaryImage=True)
            if m["m00"] > 0:
                centroid = (m["m10"] / m["m00"], m["m01"] / m["m00"])
        return MotionResult(changed, ratio, centroid, mask if keep_mask else None)
