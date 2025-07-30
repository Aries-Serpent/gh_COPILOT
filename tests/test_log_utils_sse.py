from itertools import islice
from pathlib import Path

from utils.log_utils import ensure_tables, log_event, sse_event_stream


def test_high_volume_sse(tmp_path: Path) -> None:
    db = tmp_path / "stream.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    for i in range(200):
        log_event({"details": str(i)}, table="violation_logs", db_path=db)
    gen = sse_event_stream("violation_logs", db_path=db, poll_interval=0.01)
    events = list(islice(gen, 200))
    assert len(events) == 200
