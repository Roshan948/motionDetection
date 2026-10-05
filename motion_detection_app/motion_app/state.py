"""Rest/motion state with a delay, so the label does not flicker between frames."""


class MotionState:
    def __init__(self, threshold_ratio: float, rest_delay_frames: int):
        self._threshold = threshold_ratio      # fraction of the frame area
        self._rest_delay = rest_delay_frames
        self._still_frames = 0
        self.moving = False

    def is_active(self, ratio: float) -> bool:
        """True when this single frame has enough changed area."""
        return ratio > self._threshold

    def update(self, ratio: float) -> bool:
        if self.is_active(ratio):
            self._still_frames = 0
            self.moving = True
        else:
            self._still_frames += 1
            if self._still_frames >= self._rest_delay:
                self.moving = False
        return self.moving
