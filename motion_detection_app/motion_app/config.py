"""All tunable settings live here, so no magic numbers are scattered in the code.

Every value is range-checked when the Config is created, so a bad command-line
option fails immediately with a readable message instead of a confusing error later.
"""
from __future__ import annotations

from dataclasses import dataclass


def _check(name: str, value, low, high=None) -> None:
    too_low = value < low
    too_high = high is not None and value > high
    if too_low or too_high:
        wanted = f"at least {low}" if high is None else f"between {low} and {high}"
        raise ValueError(f"{name} must be {wanted} (got {value})")


@dataclass(frozen=True)
class Config:
    # Camera
    camera_index: int = 0
    mirror: bool = True              # flip the frame so left/right match what the viewer sees
    camera_read_retries: int = 5     # failed reads tolerated in a row before giving up
    camera_retry_delay: float = 0.2  # seconds to wait between those retries

    # Preprocessing. Every frame is resized to process_width first, so all pixel-based
    # settings below behave the same on a 480p, 720p or 1080p camera.
    process_width: int = 640
    blur_kernel: int = 21            # Gaussian blur size (forced to an odd number)

    # Motion detection
    pixel_cutoff: int = 25           # brightness change needed for a pixel to count as changed
    motion_threshold_pct: float = 0.33   # percent of the frame that must change to count as motion
    rest_delay_frames: int = 10      # still frames required before switching back to rest

    # Direction tracking
    history_length: int = 6          # number of centroids compared (oldest vs newest)
    min_shift: int = 20              # dead zone in pixels (measured at process_width)
    direction_reset_frames: int = 3  # inactive frames in a row that clear the direction history

    # UI and files
    window_name: str = "Motion Detection"
    log_events: bool = False
    log_dir: str = "logs"
    max_log_files: int = 20          # older motion_events_*.csv files beyond this are deleted

    @property
    def motion_threshold_ratio(self) -> float:
        """The threshold as a fraction of the frame area (0.0033 = 0.33 percent)."""
        return self.motion_threshold_pct / 100.0

    def __post_init__(self):
        _check("camera_index", self.camera_index, 0, 20)
        _check("camera_read_retries", self.camera_read_retries, 0, 100)
        _check("camera_retry_delay", self.camera_retry_delay, 0, 5)
        _check("process_width", self.process_width, 160, 1920)
        _check("blur_kernel", self.blur_kernel, 1, 99)
        _check("pixel_cutoff", self.pixel_cutoff, 1, 255)
        _check("motion_threshold_pct", self.motion_threshold_pct, 0.01, 100)
        _check("rest_delay_frames", self.rest_delay_frames, 1, 300)
        _check("history_length", self.history_length, 2, 60)
        _check("min_shift", self.min_shift, 0, self.process_width)
        _check("direction_reset_frames", self.direction_reset_frames, 0, 300)
        _check("max_log_files", self.max_log_files, 1, 1000)
