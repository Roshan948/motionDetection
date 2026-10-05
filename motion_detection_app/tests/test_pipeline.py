import numpy as np
import pytest

from motion_app.config import Config
from motion_app.overlay import draw_status
from motion_app.pipeline import MotionPipeline

CFG = Config(motion_threshold_pct=0.33, min_shift=20, history_length=6, rest_delay_frames=3)


def frame(x=50, y=200, size=60, scale=1.0):
    """A white square on black. scale=2 gives the same scene on a 1280x960 camera."""
    w, h = int(640 * scale), int(480 * scale)
    f = np.zeros((h, w, 3), np.uint8)
    x, y, size = int(x * scale), int(y * scale), int(size * scale)
    f[y:y + size, x:x + size] = 255
    return f


def run(frames, cfg=CFG):
    p = MotionPipeline(cfg)
    return [p.process(f) for f in frames]


def test_static_scene_is_rest():
    results = run([frame()] * 6)
    assert all(not r.moving for r in results)
    assert results[-1].label == "Body in rest"


def test_moving_right():
    r = run([frame(x=50 + 15 * i) for i in range(10)])[-1]
    assert r.moving and r.direction == "Right"
    assert r.label == "Motion detected - Right"


def test_moving_left():
    r = run([frame(x=400 - 15 * i) for i in range(10)])[-1]
    assert r.moving and r.direction == "Left"


def test_moving_down():
    r = run([frame(x=300, y=50 + 15 * i) for i in range(10)])[-1]
    assert r.moving and r.direction == "Down"


def test_moving_up():
    r = run([frame(x=300, y=350 - 15 * i) for i in range(10)])[-1]
    assert r.moving and r.direction == "Up"


def test_returns_to_rest_after_motion_stops():
    frames = [frame(x=50 + 15 * i) for i in range(8)]
    frames += [frames[-1]] * 3
    results = run(frames)
    assert results[-3].moving is True      # still inside the rest delay
    assert results[-1].moving is False
    assert results[-1].direction is None


def test_direction_history_does_not_span_a_pause():
    # A long rest delay on purpose: the label stays "moving" through the pause,
    # but the old centroids must still be forgotten.
    cfg = Config(rest_delay_frames=20, direction_reset_frames=3)
    right = [frame(x=50 + 15 * i) for i in range(10)]        # ends at x = 185
    pause = [right[-1]] * 6
    left = [frame(x=185 - 15 * i) for i in range(1, 10)]
    results = run(right + pause + left, cfg)
    after_pause = results[len(right) + len(pause):]
    assert results[len(right) - 1].direction == "Right"
    assert all(r.direction is None for r in after_pause[:3])   # history is rebuilding
    assert after_pause[-1].direction == "Left"


def test_mask_only_returned_when_requested():
    p = MotionPipeline(CFG)
    p.process(frame())
    assert p.process(frame(x=80)).mask is None
    p.process(frame(x=110))
    assert p.process(frame(x=140), keep_mask=True).mask is not None


@pytest.mark.parametrize("scale", [0.5, 1.0, 1.5, 2.0])
def test_same_movement_gives_same_result_at_any_resolution(scale):
    moving = run([frame(x=50 + 15 * i, scale=scale) for i in range(10)])[-1]
    assert moving.moving and moving.direction == "Right"
    still = run([frame(scale=scale)] * 6)
    assert all(not r.moving for r in still)


def test_score_is_similar_at_different_resolutions():
    scores = {}
    for scale in (0.5, 1.0, 2.0):
        scores[scale] = run([frame(x=50 + 15 * i, scale=scale) for i in range(10)])[-1].score
    ref = scores[1.0]
    for scale, score in scores.items():
        assert abs(score - ref) / ref < 0.10, (scale, scores)


def test_overlay_draws_without_error():
    img = frame()
    before = img.copy()
    r = run([frame(x=50 + 15 * i) for i in range(10)])[-1]
    draw_status(img, r)
    assert not np.array_equal(img, before)
