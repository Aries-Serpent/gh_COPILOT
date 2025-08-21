import sqlite3
import datetime
from pathlib import Path

from itertools import islice

from utils.log_utils import ensure_tables, log_event, log_stream


def test_high_frequency_logging(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    db = tmp_path / "hf.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    for i in range(100):
        log_event({"details": str(i)}, table="violation_logs", db_path=db)
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM violation_logs").fetchone()[0]
    assert count == 100


def test_log_recovery_after_interruption(tmp_path: Path) -> None:
    db = tmp_path / "recover.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    conn = sqlite3.connect(db)
    for i in range(5):
        conn.execute(
            "INSERT INTO violation_logs (details, timestamp) VALUES (?, ?)",
            (
                str(i),
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ),
        )
    conn.commit()
    conn.close()
    events = list(islice(log_stream("violation_logs", db_path=db, poll_interval=0.1), 5))
    assert len(events) == 5
