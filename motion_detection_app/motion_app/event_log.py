"""Optional CSV log of state changes (not every frame). Only text is saved, never video."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .pipeline import FrameResult


class LogError(RuntimeError):
    """The event log could not be created."""


class EventLogger:
    def __init__(self, directory: str = "logs", max_files: int = 20):
        folder = Path(directory)
        self._disabled = False
        self._last = None
        try:
            folder.mkdir(parents=True, exist_ok=True)
            self.path, self._file = self._create(folder)
            self._writer = csv.writer(self._file)
            self._writer.writerow(["timestamp", "state", "direction", "changed_percent"])
            self._file.flush()
            self._prune(folder, max_files)
        except OSError as err:
            raise LogError(f"Could not create the event log in '{folder}': {err}") from err

    @staticmethod
    def _create(folder: Path):
        """Open a brand-new file. Mode 'x' refuses to overwrite, so two runs can never collide."""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        for n in range(100):
            suffix = "" if n == 0 else f"_{n}"
            path = folder / f"motion_events_{stamp}{suffix}.csv"
            try:
                return path, open(path, "x", newline="", encoding="utf-8")
            except FileExistsError:
                continue
        raise FileExistsError("could not find a free log file name")

    @staticmethod
    def _prune(folder: Path, max_files: int) -> None:
        """Keep only the newest max_files logs (names sort by creation time)."""
        logs = sorted(folder.glob("motion_events_*.csv"), key=lambda p: p.name)
        for old in logs[:-max_files]:
            try:
                old.unlink()
            except OSError:
                pass   # in use by another running copy, or no permission: leave it

    def log(self, result: FrameResult) -> None:
        if self._disabled:
            return
        key = (result.moving, result.direction)
        if key == self._last:
            return
        self._last = key
        try:
            self._writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                "motion" if result.moving else "rest",
                result.direction or "",
                f"{result.score:.2f}",
            ])
            self._file.flush()
        except OSError as err:
            self._disabled = True
            print(f"Warning: event logging stopped because the file could not be written ({err}).")

    def close(self) -> None:
        try:
            self._file.close()
        except OSError:
            pass
