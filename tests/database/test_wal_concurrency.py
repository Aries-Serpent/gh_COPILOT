import os
import threading
import time
from pathlib import Path

from enterprise_modules.database_utils import (
    execute_safe_batch_insert,
    get_enterprise_database_connection,
)


def test_wal_mode_and_busy_timeout(tmp_path):
    db = tmp_path / "t.db"
    with get_enterprise_database_connection(db) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
    assert mode.lower() == "wal"
    assert timeout == 30000


def test_concurrent_reads_and_writes():
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE"))
    db = workspace / "tmp" / "wal_concurrency.db"
    db.parent.mkdir(exist_ok=True)
    db.unlink(missing_ok=True)
    with get_enterprise_database_connection(db) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.commit()

    errors: list[Exception] = []

    def writer() -> None:
        try:
            conn = get_enterprise_database_connection(db)
            execute_safe_batch_insert(
                conn,
                "t",
                [{"id": i} for i in range(100)],
                chunk_size=10,
                checkpoint_interval=50,
            )
            conn.close()
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    def reader() -> None:
        try:
            conn = get_enterprise_database_connection(db)
            for _ in range(20):
                conn.execute("SELECT COUNT(*) FROM t").fetchone()
                time.sleep(0.01)
            conn.close()
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    t_w = threading.Thread(target=writer)
    t_r = threading.Thread(target=reader)
    t_w.start()
    t_r.start()
    t_w.join()
    t_r.join()

    assert not errors
    with get_enterprise_database_connection(db) as conn:
        total = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert total == 100
    db.unlink(missing_ok=True)
