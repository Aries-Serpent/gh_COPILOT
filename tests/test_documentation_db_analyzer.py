import sqlite3
from pathlib import Path

from scripts.database.documentation_db_analyzer import (
    analyze_documentation_gaps,
    validate_analysis,
)


def test_documentation_db_analyzer(tmp_path: Path) -> None:
    docdb = tmp_path / "documentation.db"
    with sqlite3.connect(docdb) as conn:
        conn.execute("CREATE TABLE documentation (title TEXT, content TEXT)")
        conn.executemany(
            "INSERT INTO documentation (title, content) VALUES (?, ?)",
            [("A", ""), ("B", "content")],
        )
    analytics = tmp_path / "analytics.db"
    log_dir = tmp_path / "logs" / "template_rendering"
    results = analyze_documentation_gaps([docdb], analytics, log_dir)
    assert results[0]["gaps"] == 1
    assert any(log_dir.iterdir())
    assert validate_analysis(analytics, 1)
