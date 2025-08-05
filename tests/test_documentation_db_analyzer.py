import sqlite3
from pathlib import Path

from scripts.database.documentation_db_analyzer import (
    analyze_documentation_gaps,
    analyze_documentation_tables,
    validate_analysis,
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
    results = analyze_documentation_gaps([docdb], analytics, log_dir)
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
    dummy = type(
        "D", (), {"called": False, "validate_corrections": lambda self, files: setattr(self, "called", True) or True}
    )()
    import importlib

    module = importlib.import_module("scripts.database.documentation_db_analyzer")
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
    dummy = type(
        "D", (), {"called": False, "validate_corrections": lambda self, files: setattr(self, "called", True) or True}
    )()
    import importlib

    module = importlib.import_module("scripts.database.documentation_db_analyzer")
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
    dummy = type(
        "D", (), {"called": False, "validate_corrections": lambda self, files: setattr(self, "called", True) or True}
    )()
    import scripts.database.documentation_db_analyzer as mod

    monkeypatch.setattr(mod, "SecondaryCopilotValidator", lambda: dummy)
    assert validate_analysis(analytics, 1)
    assert dummy.called
