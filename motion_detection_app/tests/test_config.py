import pytest

from motion_app.config import Config


def test_defaults_are_valid():
    cfg = Config()
    assert cfg.motion_threshold_ratio == pytest.approx(0.0033)


@pytest.mark.parametrize("name, value", [
    ("camera_index", -1),
    ("camera_index", 99),
    ("camera_read_retries", -1),
    ("camera_retry_delay", -0.5),
    ("process_width", 10),
    ("process_width", 100000),
    ("blur_kernel", 0),
    ("blur_kernel", 501),
    ("pixel_cutoff", 0),
    ("pixel_cutoff", 300),
    ("motion_threshold_pct", 0),
    ("motion_threshold_pct", 150),
    ("rest_delay_frames", 0),
    ("history_length", 1),
    ("min_shift", -1),
    ("direction_reset_frames", -1),
    ("max_log_files", 0),
])
def test_out_of_range_values_are_rejected_with_a_readable_message(name, value):
    with pytest.raises(ValueError, match=name):
        Config(**{name: value})


def test_message_states_the_allowed_range():
    with pytest.raises(ValueError, match=r"blur_kernel must be between 1 and 99 \(got 500\)"):
        Config(blur_kernel=500)


def test_min_shift_cannot_exceed_process_width():
    with pytest.raises(ValueError, match="min_shift"):
        Config(process_width=320, min_shift=400)
