import sqlite3
from pathlib import Path
from typing import Any

from scripts.database.maintenance_scheduler import run_cycle
from scripts.database.unified_database_initializer import initialize_database


class DummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(self, *args: Any, total: int, desc: str, unit: str = "task", **kwargs: Any) -> None:
        self.total = total
        self.desc = desc
        self.unit = unit
        self.updates = 0

    def __enter__(self) -> "DummyTqdm":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def update(self, n: int = 1) -> None:
        self.updates += n

    @property
    def format_dict(self) -> dict:
        return {"elapsed": 0, "remaining": 0}

    def set_postfix_str(self, *args: str, **kwargs: str) -> None:
        pass


def test_run_cycle(tmp_path: Path, monkeypatch) -> None:
    db_dir = tmp_path / "databases"
    docs_dir = tmp_path / "documentation"
    db_dir.mkdir()
    docs_dir.mkdir()

    master = db_dir / "enterprise_assets.db"
    replica = db_dir / "replica.db"
    log_db = master
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    initialize_database(log_db)

    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")

    list_file = docs_dir / "CONSOLIDATED_DATABASE_LIST.md"
    list_file.write_text("- enterprise_assets.db  # Size: 0.01 MB\n- replica.db  # Size: 0.01 MB\n")

    run_cycle(tmp_path)

    with sqlite3.connect(replica) as conn:
        count = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert count == 1


def test_run_cycle_logging_and_progress(tmp_path: Path, monkeypatch) -> None:
    db_dir = tmp_path / "databases"
    docs_dir = tmp_path / "documentation"
    db_dir.mkdir()
    docs_dir.mkdir()

    master = db_dir / "enterprise_assets.db"
    log_db = master
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    initialize_database(log_db)

    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")

    list_file = docs_dir / "CONSOLIDATED_DATABASE_LIST.md"
    list_file.write_text("- enterprise_assets.db  # Size: 0.01 MB\n- replica.db  # Size: 0.01 MB\n")

    bars: list[DummyTqdm] = []

    def dummy_tqdm(*args: Any, **kwargs: Any) -> DummyTqdm:
        bar = DummyTqdm(*args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr("scripts.database.maintenance_scheduler.tqdm", dummy_tqdm)

    run_cycle(tmp_path)

    assert bars and bars[0].updates == 3
    with sqlite3.connect(log_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]
    assert count >= 3
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consistency_audit_events(
              id INTEGER PRIMARY KEY, started_at TEXT, finished_at TEXT,
              scanned_paths TEXT, missing_count INTEGER, stale_count INTEGER,
              regenerated_count INTEGER, reingested_count INTEGER,
              details_json TEXT, status TEXT
            )
            """
        )
    run_cycle(tmp_path)
    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute(
            "SELECT COUNT(*) FROM consistency_audit_events"
        ).fetchone()[0]
    assert rows >= 1
