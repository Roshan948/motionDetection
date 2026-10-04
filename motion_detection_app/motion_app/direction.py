"""Stages 6 to 8 - track the motion centroid and turn its shift into a direction."""
from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Tuple


class DirectionTracker:
    """Compares the oldest and newest of the last N centroids.

    Image coordinates start at the top-left corner, so a positive dy means the
    motion is going DOWN the screen.
    """

    def __init__(self, history_length: int = 6, min_shift: int = 20):
        self._history: Deque[Tuple[float, float]] = deque(maxlen=history_length)
        self._min_shift = min_shift

    def update(self, centroid: Tuple[float, float]) -> Optional[str]:
        self._history.append(centroid)
        if len(self._history) < self._history.maxlen:
            return None

        dx = self._history[-1][0] - self._history[0][0]
        dy = self._history[-1][1] - self._history[0][1]
        if max(abs(dx), abs(dy)) <= self._min_shift:   # inside the dead zone
            return None
        if abs(dx) > abs(dy):
            return "Right" if dx > 0 else "Left"
        return "Down" if dy > 0 else "Up"

    def reset(self) -> None:
        self._history.clear()
