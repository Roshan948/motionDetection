import pytest

from motion_app.event_log import EventLogger, LogError
from motion_app.pipeline import FrameResult


def result(moving, direction=None, score=1.0):
    return FrameResult(moving, direction, score)


def test_two_loggers_never_share_a_file(tmp_path):
    a = EventLogger(str(tmp_path), max_files=50)
    b = EventLogger(str(tmp_path), max_files=50)
    c = EventLogger(str(tmp_path), max_files=50)
    paths = {a.path, b.path, c.path}
    for lg in (a, b, c):
        lg.close()
    assert len(paths) == 3
    assert len(list(tmp_path.glob("motion_events_*.csv"))) == 3


def test_old_logs_are_pruned(tmp_path):
    for _ in range(5):
        EventLogger(str(tmp_path), max_files=2).close()
    assert len(list(tmp_path.glob("motion_events_*.csv"))) == 2


def test_only_state_changes_are_written(tmp_path):
    lg = EventLogger(str(tmp_path))
    for r in (result(False), result(False), result(True, "Left"), result(True, "Left"), result(False)):
        lg.log(r)
    lg.close()
    rows = lg.path.read_text(encoding="utf-8").strip().splitlines()
    assert rows[0] == "timestamp,state,direction,changed_percent"
    assert [row.split(",")[1] for row in rows[1:]] == ["rest", "motion", "rest"]


def test_unusable_folder_gives_a_readable_error(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    with pytest.raises(LogError, match="Could not create the event log"):
        EventLogger(str(blocker / "logs"))
