import json
import sqlite3
from pathlib import Path

from scripts.code_placeholder_audit import (
    fetch_db_placeholders,
    log_findings,
    update_dashboard,
)


def test_fetch_db_placeholders(tmp_path: Path) -> None:
    db = tmp_path / "prod.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT)"
        )
        conn.execute(
            "INSERT INTO template_placeholders VALUES ('STUB_PLACE')"
        )
    assert fetch_db_placeholders(db) == ["STUB_PLACE"]


def test_log_findings_and_update_dashboard(tmp_path: Path) -> None:
    analytics = tmp_path / "analytics.db"
    dashboard = tmp_path / "dash"
    results = [
        {"file": "f.py", "line": 1, "pattern": "TODO", "context": "todo"},
        {"file": "g.py", "line": 2, "pattern": "FIXME", "context": "fix"},
    ]
    log_findings(results, analytics, simulate=False)
    with sqlite3.connect(analytics) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM code_audit_log")
        assert cur.fetchone()[0] == len(results)
    update_dashboard(len(results), dashboard)
    summary = json.loads((dashboard / "placeholder_summary.json").read_text())
    assert summary["findings"] == len(results)
