"""All tunable settings live here, so no magic numbers are scattered in the code."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Camera
    camera_index: int = 0
    mirror: bool = True            # flip the frame so left/right match what the viewer sees

    # Preprocessing
    blur_kernel: int = 21          # Gaussian blur size (forced to an odd number)

    # Motion detection
    pixel_cutoff: int = 25         # brightness change needed for a pixel to count as changed
    motion_threshold: int = 1000   # changed pixels needed to call a frame "motion"
    rest_delay_frames: int = 10    # still frames required before switching back to rest

    # Direction tracking
    history_length: int = 6        # number of centroids compared (oldest vs newest)
    min_shift: int = 20            # dead zone in pixels; smaller shifts report no direction

    # UI and files
    window_name: str = "Motion Detection"
    log_events: bool = False
    log_dir: str = "logs"

    def __post_init__(self):
        if self.history_length < 2:
            raise ValueError("history_length must be at least 2")
        if self.motion_threshold < 1:
            raise ValueError("motion_threshold must be positive")
        if self.rest_delay_frames < 1:
            raise ValueError("rest_delay_frames must be at least 1")
        if self.min_shift < 0:
            raise ValueError("min_shift cannot be negative")
