from motion_app.direction import DirectionTracker


def feed(tracker, points):
    out = None
    for p in points:
        out = tracker.update(p)
    return out


def test_right():
    t = DirectionTracker(6, 20)
    assert feed(t, [(100 + 15 * i, 200) for i in range(6)]) == "Right"


def test_left():
    t = DirectionTracker(6, 20)
    assert feed(t, [(300 - 15 * i, 200) for i in range(6)]) == "Left"


def test_down_is_positive_y():
    t = DirectionTracker(6, 20)
    assert feed(t, [(200, 100 + 15 * i) for i in range(6)]) == "Down"


def test_up():
    t = DirectionTracker(6, 20)
    assert feed(t, [(200, 300 - 15 * i) for i in range(6)]) == "Up"


def test_small_shift_has_no_direction():
    t = DirectionTracker(6, 20)
    assert feed(t, [(100 + i, 100) for i in range(6)]) is None


def test_needs_full_history():
    t = DirectionTracker(6, 20)
    assert feed(t, [(100 + 30 * i, 100) for i in range(5)]) is None


def test_reset_clears_history():
    t = DirectionTracker(3, 5)
    feed(t, [(0, 0), (50, 0), (100, 0)])
    t.reset()
    assert t.update((100, 0)) is None
