from pathlib import Path
import sqlite3
import threading
import time

from scripts.database.watch_sync_pairs import run_watch_pairs


def _create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO items (data) VALUES ('x')")
        conn.commit()


def test_threads_exit_on_stop(tmp_path: Path) -> None:
    db1_a = tmp_path / "a1.db"
    db1_b = tmp_path / "b1.db"
    db2_a = tmp_path / "a2.db"
    db2_b = tmp_path / "b2.db"
    for p in (db1_a, db1_b, db2_a, db2_b):
        _create_db(p)

    stop = threading.Event()
    t = threading.Thread(
        target=run_watch_pairs,
        args=([(db1_a, db1_b), (db2_a, db2_b)],),
        kwargs={"interval": 0.1, "stop_event": stop},
    )
    t.start()
    time.sleep(0.3)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()

