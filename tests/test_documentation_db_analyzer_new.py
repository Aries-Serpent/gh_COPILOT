import shutil
import sqlite3
from pathlib import Path

from scripts.database.documentation_db_analyzer import audit_placeholders, rollback_cleanup


def test_audit_placeholders(tmp_path: Path) -> None:
    db = tmp_path / "doc.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (content TEXT)")
        conn.executemany("INSERT INTO enterprise_documentation VALUES (?)", [("todo fix",), ("ok",)])
    count = audit_placeholders(db)
    assert count == 1


def test_rollback_cleanup(tmp_path: Path) -> None:
    db = tmp_path / "doc.db"
    backup = tmp_path / "backup.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE t(a TEXT)")
        conn.execute("INSERT INTO t VALUES ('x')")
    shutil.copy2(db, backup)
    with sqlite3.connect(db) as conn:
        conn.execute("DELETE FROM t")
    assert rollback_cleanup(db, backup)
    with sqlite3.connect(db) as conn:
        val = conn.execute("SELECT a FROM t").fetchone()[0]
    assert val == "x"


def test_analyze_and_cleanup_logs_corrections(tmp_path: Path) -> None:
    db = tmp_path / "doc.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_type TEXT, source_path TEXT, title TEXT, content TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?, ?, ?, ?)",
            [
                ("BACKUP_LOG", "x", "a", "foo"),
                ("DOC", "y", "b", "bar"),
                ("DOC", "y", "b", "bar"),
            ],
        )
    import importlib
    from scripts import database

    module = importlib.import_module("scripts.database.documentation_db_analyzer")
    module.ANALYTICS_DB = analytics
    module.ensure_correction_history(analytics)
    report = module.analyze_and_cleanup(db)
    assert report["removed_duplicates"] or report["removed_backups"]
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT violation_code FROM correction_history").fetchall()
    assert rows
