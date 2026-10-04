import numpy as np

from motion_app.config import Config
from motion_app.overlay import draw_status
from motion_app.pipeline import MotionPipeline

CFG = Config(motion_threshold=1000, min_shift=20, history_length=6, rest_delay_frames=3)


def frame(x=50, y=200, size=60):
    f = np.zeros((480, 640, 3), np.uint8)
    f[y:y + size, x:x + size] = 255
    return f


def run(frames):
    p = MotionPipeline(CFG)
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


def test_overlay_draws_without_error():
    img = frame()
    before = img.copy()
    r = run([frame(x=50 + 15 * i) for i in range(10)])[-1]
    draw_status(img, r)
    assert not np.array_equal(img, before)
