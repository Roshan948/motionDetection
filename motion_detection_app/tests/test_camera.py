import numpy as np
import pytest

import motion_app.camera as camera_module
from motion_app.camera import Camera, CameraError


class FakeCapture:
    def __init__(self, script, opened=True):
        self.script = list(script)       # True = good frame, False = failed read
        self.opened = opened
        self.reads = 0
        self.released = False

    def isOpened(self):
        return self.opened

    def read(self):
        self.reads += 1
        ok = self.script.pop(0) if self.script else False
        return ok, (np.zeros((4, 4, 3), np.uint8) if ok else None)

    def release(self):
        self.released = True


def use(monkeypatch, cap):
    monkeypatch.setattr(camera_module.cv2, "VideoCapture", lambda index: cap)


def test_open_failure_gives_a_clear_error(monkeypatch):
    cap = FakeCapture([], opened=False)
    use(monkeypatch, cap)
    with pytest.raises(CameraError, match="Could not open camera 0"):
        Camera(0).open()
    assert cap.released


def test_a_temporary_read_failure_is_retried(monkeypatch):
    cap = FakeCapture([False, False, True])
    use(monkeypatch, cap)
    with Camera(0, retries=3, retry_delay=0) as camera:
        frame = camera.read()
    assert frame.shape == (4, 4, 3)
    assert cap.reads == 3


def test_a_permanent_read_failure_stops_after_the_retries(monkeypatch):
    cap = FakeCapture([])
    use(monkeypatch, cap)
    with pytest.raises(CameraError, match="stopped delivering frames"):
        with Camera(0, retries=2, retry_delay=0) as camera:
            camera.read()
    assert cap.reads == 3            # first try + 2 retries
    assert cap.released              # the context manager still released the camera


def test_reading_before_opening_is_an_error():
    with pytest.raises(CameraError):
        Camera(0).read()
