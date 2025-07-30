from pathlib import Path

from utils.log_utils import log_event, stream_events, ensure_tables


def test_log_and_stream(tmp_path: Path) -> None:
    db = tmp_path / "a.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    for i in range(3):
        log_event({"details": str(i)}, table="violation_logs", db_path=db)
    events = list(stream_events("violation_logs", db_path=db))
    assert len(events) == 3
    assert "data:" in events[0]
