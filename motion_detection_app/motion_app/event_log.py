"""Optional CSV log of state changes (not every frame)."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .pipeline import FrameResult


class EventLogger:
    def __init__(self, directory: str = "logs"):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        self.path = folder / f"motion_events_{datetime.now():%Y%m%d_%H%M%S}.csv"
        self._file = open(self.path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["timestamp", "state", "direction", "score"])
        self._last = None

    def log(self, result: FrameResult) -> None:
        key = (result.moving, result.direction)
        if key == self._last:
            return
        self._last = key
        self._writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            "motion" if result.moving else "rest",
            result.direction or "",
            result.score,
        ])
        self._file.flush()

    def close(self) -> None:
        self._file.close()
