import sqlite3
from pathlib import Path

import logging
import time

from tqdm import tqdm

from scripts.database.add_code_audit_log import add_table, ensure_code_audit_log
from secondary_copilot_validator import SecondaryCopilotValidator


def test_add_code_audit_log(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE placeholder_audit (id INTEGER)")
    # run migration twice to ensure idempotence
    add_table(db)
    ensure_code_audit_log(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp)"
            " VALUES ('f', 1, 'TODO', 'ctx', 'ts')"
        )
        rows = conn.execute("SELECT file_path FROM code_audit_log").fetchall()
    assert rows


def test_ensure_code_audit_log_wrapper(tmp_path: Path) -> None:
    """Ensure wrapper delegates to ``add_table``."""
    db = tmp_path / "analytics.db"
    ensure_code_audit_log(db)
    with sqlite3.connect(db) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' and name='code_audit_log'").fetchall()
    assert tables


def test_add_code_audit_log_dual_copilot(tmp_path: Path, caplog) -> None:
    """Verify migration with dual copilot validation."""
    db = tmp_path / "analytics.db"
    caplog.set_level(logging.INFO)

    # Primary copilot: run migration with visual indicators
    start = time.time()
    for _ in tqdm(range(1), desc="Simulating migration steps", unit="step"):
        add_table(db)

    # Secondary copilot: validate table exists and script passes flake8
    with sqlite3.connect(db) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' and name='code_audit_log'").fetchall()

    validator = SecondaryCopilotValidator(logging.getLogger(__name__))
    script = Path(__file__).resolve().parents[1] / "scripts" / "database" / "add_code_audit_log.py"
    validation = validator.validate_corrections([str(script)])

    elapsed = time.time() - start

    assert tables
    assert validation
    assert "add_table" in caplog.text or "code_audit_log ensured" in caplog.text
    assert elapsed >= 0


def test_sql_migration_dual_copilot(tmp_path: Path) -> None:
    """Run SQL migration with secondary validation."""
    repo_root = Path(__file__).resolve().parents[1]
    db = tmp_path / "analytics.db"

    sql = (repo_root / "databases" / "migrations" / "add_code_audit_log.sql").read_text()

    start_time = time.time()
    with sqlite3.connect(db) as conn, tqdm(total=1, desc="apply-sql", unit="step") as bar:
        conn.executescript(sql)
        bar.update(1)
        conn.commit()

    with sqlite3.connect(db) as conn:
        exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' and name='code_audit_log'").fetchall()
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]

    duration = time.time() - start_time
    assert exists
    assert integrity == "ok"
    assert duration >= 0
