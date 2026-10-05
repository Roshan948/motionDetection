import numpy as np

from motion_app.detector import MotionDetector
from motion_app.state import MotionState


def test_first_frame_has_no_motion():
    r = MotionDetector(25).analyse(np.zeros((100, 100), np.uint8))
    assert r.changed_pixels == 0 and r.ratio == 0.0 and r.centroid is None


def test_changed_area_gives_score_ratio_and_centroid():
    d = MotionDetector(25)
    blank = np.zeros((100, 100), np.uint8)
    d.analyse(blank)
    img = blank.copy()
    img[40:60, 60:80] = 255
    r = d.analyse(img)
    assert r.changed_pixels == 400
    assert r.ratio == 400 / 10000
    assert abs(r.centroid[0] - 69.5) < 1 and abs(r.centroid[1] - 49.5) < 1


def test_ratio_is_independent_of_frame_size():
    """The same share of the frame changing gives the same ratio at any size."""
    ratios = []
    for size in (100, 200, 400):
        d = MotionDetector(25)
        blank = np.zeros((size, size), np.uint8)
        d.analyse(blank)
        img = blank.copy()
        q = size // 4
        img[:q, :] = 255                      # top quarter of the frame changes
        ratios.append(d.analyse(img).ratio)
    assert ratios == [0.25, 0.25, 0.25]


def test_identical_frames_have_no_motion():
    d = MotionDetector(25)
    blank = np.zeros((50, 50), np.uint8)
    d.analyse(blank)
    r = d.analyse(blank)
    assert r.changed_pixels == 0 and r.centroid is None


def test_mask_is_only_returned_when_requested():
    d = MotionDetector(25)
    blank = np.zeros((50, 50), np.uint8)
    moved = blank.copy()
    moved[10:20, 10:20] = 255
    d.analyse(blank)
    assert d.analyse(moved).mask is None
    d.analyse(blank)
    assert d.analyse(moved, keep_mask=True).mask is not None


def test_resolution_change_restarts_comparison_instead_of_crashing():
    d = MotionDetector(25)
    d.analyse(np.zeros((50, 50), np.uint8))
    r = d.analyse(np.zeros((60, 80), np.uint8))
    assert r.changed_pixels == 0


def test_state_waits_before_returning_to_rest():
    s = MotionState(threshold_ratio=0.01, rest_delay_frames=3)
    assert s.update(0.05) is True
    assert s.update(0.0) is True
    assert s.update(0.0) is True
    assert s.update(0.0) is False
