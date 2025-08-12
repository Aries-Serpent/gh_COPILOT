import sqlite3
import os
from pathlib import Path

from scripts.database.documentation_db_analyzer import (
    analyze_documentation_tables,
    validate_analysis,
    rollback_db,
    summarize_corrections,
    ensure_correction_history,
)


def test_documentation_db_analyzer(tmp_path: Path) -> None:
    docdb = tmp_path / "documentation.db"
    with sqlite3.connect(docdb) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (title TEXT, content TEXT)")
        conn.executemany(
            "INSERT INTO enterprise_documentation (title, content) VALUES (?, ?)",
            [("A", ""), ("B", "content")],
        )
    analytics = tmp_path / "analytics.db"
    log_dir = tmp_path / "logs" / "template_rendering"
    import scripts.database.documentation_db_analyzer as module
    module.SecondaryCopilotValidator = lambda: type("D", (), {"validate_corrections": lambda self, files: True})()
    results = module.analyze_documentation_gaps([docdb], analytics, log_dir)
    assert results[0]["gaps"] == 1
    assert any(log_dir.iterdir())
    assert validate_analysis(analytics, 1)


def test_analyze_documentation_gaps_runs_validator(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "doc.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (title TEXT, content TEXT)")
        conn.execute("INSERT INTO enterprise_documentation VALUES ('A', '')")
    analytics = tmp_path / "analytics.db"
    log_dir = tmp_path / "logs"
    from types import SimpleNamespace

    dummy = SimpleNamespace(called=False)

    def _validate(self, files):
        self.called = True
        return True

    dummy.validate_corrections = _validate.__get__(dummy, SimpleNamespace)
    import scripts.database.documentation_db_analyzer as module
    monkeypatch.setattr(module, "SecondaryCopilotValidator", lambda: dummy)
    module.ANALYTICS_DB = analytics
    module.analyze_documentation_gaps([db], analytics, log_dir)
    assert dummy.called


def test_analyzer_runs_validator_and_logs(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "doc.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (title TEXT, content TEXT)")
        conn.execute("INSERT INTO enterprise_documentation VALUES ('A', 'foo')")
    analytics = tmp_path / "analytics.db"
    from types import SimpleNamespace

    dummy = SimpleNamespace(called=False)

    def _validate(self, files):
        self.called = True
        return True

    dummy.validate_corrections = _validate.__get__(dummy, SimpleNamespace)
    import scripts.database.documentation_db_analyzer as module
    monkeypatch.setattr(module, "SecondaryCopilotValidator", lambda: dummy)
    module.ANALYTICS_DB = analytics
    analyze_documentation_tables([db], analytics)
    assert dummy.called
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM doc_analysis").fetchone()[0]
    assert count == 1


def test_validate_analysis_runs_validator(tmp_path: Path, monkeypatch) -> None:
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE doc_audit (id INTEGER)")
        conn.execute("INSERT INTO doc_audit VALUES (1)")
    from types import SimpleNamespace

    dummy = SimpleNamespace(called=False)

    def _validate(self, files):
        self.called = True
        return True

    dummy.validate_corrections = _validate.__get__(dummy, SimpleNamespace)
    import scripts.database.documentation_db_analyzer as mod

    monkeypatch.setattr(mod, "SecondaryCopilotValidator", lambda: dummy)
    assert validate_analysis(analytics, 1)
    assert dummy.called


def test_rollback_records_session(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "doc.db"
    backup = tmp_path / "doc.bak"
    analytics = tmp_path / "analytics.db"
    db.write_text("data")
    backup.write_text("backup")
    import scripts.database.documentation_db_analyzer as mod

    monkeypatch.setattr(mod, "ANALYTICS_DB", analytics)
    monkeypatch.setattr(mod, "REPORTS_DIR", tmp_path / "reports")
    result = mod.rollback_cleanup(db, backup)
    assert result
    assert (tmp_path / "reports" / "correction_sessions.csv").exists()
    with sqlite3.connect(analytics) as conn:
        row = conn.execute("SELECT COUNT(*) FROM correction_sessions").fetchone()[0]
    assert row == 1


def test_rollback_db_records_session(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "doc.db"
    backup = tmp_path / "doc.bak"
    analytics = tmp_path / "analytics.db"
    db.write_text("data")
    backup.write_text("backup")
    import scripts.database.documentation_db_analyzer as mod

    monkeypatch.setattr(mod, "ANALYTICS_DB", analytics)
    monkeypatch.setattr(mod, "REPORTS_DIR", tmp_path / "reports")
    mod.rollback_db(db, backup)
    assert (tmp_path / "reports" / "correction_sessions.csv").exists()
    with sqlite3.connect(analytics) as conn:
        row = conn.execute("SELECT COUNT(*) FROM correction_sessions").fetchone()[0]
    assert row == 1


def test_summarize_and_rollback_logging(tmp_path: Path) -> None:
    analytics_dir = tmp_path / "databases"
    analytics_dir.mkdir()
    analytics = analytics_dir / "analytics.db"
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    ensure_correction_history(analytics)
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, violations_count, fixes_applied, fix_rate, timestamp) VALUES (?,?,?,?,?,?,?,?)",
            ("s1", "f", "X", "fix", 2, 1, 0.5, "ts"),
        )
        conn.execute(
            "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, violations_count, fixes_applied, fix_rate, timestamp) VALUES (?,?,?,?,?,?,?,?)",
            ("s2", "f", "DOC_ROLLBACK", "DATABASE_RESTORE", 1, 1, 1.0, "ts"),
        )
        conn.commit()

    reports_dir = tmp_path / "reports"
    summary = summarize_corrections(analytics, reports_dir)
    assert summary["entries"] == 2
    assert summary["violations"] == 3
    assert summary["fixes"] == 2
    assert summary["rollbacks"] == 1
    assert list(reports_dir.glob("correction_summary_*.json"))
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM doc_analysis").fetchone()[0]
    assert count >= 1

    db = tmp_path / "db.sqlite"
    backup = tmp_path / "db.bak"
    db.write_text("x")
    backup.write_text("y")
    import scripts.database.documentation_db_analyzer as mod
    mod.ANALYTICS_DB = analytics
    rollback_db(db, backup)
    with sqlite3.connect(analytics) as conn:
        count2 = conn.execute("SELECT COUNT(*) FROM doc_analysis").fetchone()[0]
    assert count2 >= count
