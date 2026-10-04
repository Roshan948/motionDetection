import numpy as np

from motion_app.detector import MotionDetector
from motion_app.state import MotionState


def test_first_frame_has_no_motion():
    r = MotionDetector(25).analyse(np.zeros((100, 100), np.uint8))
    assert r.score == 0 and r.centroid is None


def test_changed_area_gives_score_and_centroid():
    d = MotionDetector(25)
    blank = np.zeros((100, 100), np.uint8)
    d.analyse(blank)
    img = blank.copy()
    img[40:60, 60:80] = 255
    r = d.analyse(img)
    assert r.score == 400
    assert abs(r.centroid[0] - 69.5) < 1 and abs(r.centroid[1] - 49.5) < 1


def test_identical_frames_have_no_motion():
    d = MotionDetector(25)
    blank = np.zeros((50, 50), np.uint8)
    d.analyse(blank)
    r = d.analyse(blank)
    assert r.score == 0 and r.centroid is None


def test_state_waits_before_returning_to_rest():
    s = MotionState(threshold=100, rest_delay_frames=3)
    assert s.update(500) is True
    assert s.update(0) is True
    assert s.update(0) is True
    assert s.update(0) is False
