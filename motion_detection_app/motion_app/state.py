"""Rest/motion state with a delay, so the label does not flicker between frames."""


class MotionState:
    def __init__(self, threshold: int, rest_delay_frames: int):
        self._threshold = threshold
        self._rest_delay = rest_delay_frames
        self._still_frames = 0
        self.moving = False

    def is_active(self, score: int) -> bool:
        """True when this single frame has enough changed pixels."""
        return score > self._threshold

    def update(self, score: int) -> bool:
        if self.is_active(score):
            self._still_frames = 0
            self.moving = True
        else:
            self._still_frames += 1
            if self._still_frames >= self._rest_delay:
                self.moving = False
        return self.moving
