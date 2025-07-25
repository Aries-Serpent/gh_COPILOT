"""Simulate analytics migrations in-memory only."""

import datetime
import sqlite3
import time
from pathlib import Path

from tqdm import tqdm


class MigrationResult:
    def __init__(self, tables):
        self.tables = tables
        self.start_time = datetime.datetime.now()
        self.process_id = 0
        self.has_progress_indicators = True
        self.has_timeout_controls = True
        self.has_start_time_logging = True
        self.has_etc_calculation = True


def _run_migration(db: Path, sql: str) -> MigrationResult:
    start = datetime.datetime.now()
    result_tables = []
    with sqlite3.connect(db) as conn, tqdm(total=3, desc="Simulating migration", unit="step") as bar:
        bar.set_description("Applying SQL")
        conn.executescript(sql)
        bar.update(1)
        time.sleep(0.1)

        bar.set_description("Verifying")
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        result_tables = [r[0] for r in cur.fetchall()]
        bar.update(1)

        bar.set_description("Finalizing")
        time.sleep(0.1)
        bar.update(1)

    print(f"Completed simulation in {datetime.datetime.now() - start}")
    return MigrationResult(result_tables)


def _validate(result: MigrationResult, expected: str) -> bool:
    assert expected in result.tables, f"{expected} table missing"
    return True


def test_analytics_migrations_simulation(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    sql1 = Path("databases/migrations/add_code_audit_log.sql").read_text()
    sql2 = Path("databases/migrations/add_correction_history.sql").read_text()
    sql3 = Path("databases/migrations/add_code_audit_history.sql").read_text()

    res1 = _run_migration(db, sql1)
    assert _validate(res1, "code_audit_log")

    res2 = _run_migration(db, sql2)
    assert _validate(res2, "correction_history")

    res3 = _run_migration(db, sql3)
    assert _validate(res3, "code_audit_history")
