import json
import sqlite3
from pathlib import Path

from scripts.code_placeholder_audit import (
    fetch_db_placeholders,
    log_findings,
    update_dashboard,
    scan_file_for_placeholders,
)


def test_fetch_db_placeholders(tmp_path: Path) -> None:
    db = tmp_path / "prod.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE template_placeholders (placeholder_name TEXT)")
        conn.execute("INSERT INTO template_placeholders VALUES ('STUB_PLACE')")
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
    update_dashboard(len(results), dashboard, analytics)
    summary = json.loads((dashboard / "placeholder_summary.json").read_text())
    assert summary["findings"] == len(results)
    assert summary["resolved_count"] == 0
    assert summary["progress_status"] in {"issues_pending", "complete"}
    assert summary["compliance_status"] == "non_compliant"
    assert summary["placeholder_counts"] == {"TODO": 1, "FIXME": 1}


def test_scan_file_for_placeholders(tmp_path: Path) -> None:
    target = tmp_path / "demo.py"
    target.write_text("def x():\n    pass  # TODO something\n")
    findings = scan_file_for_placeholders(target)
    patterns = {f["pattern"] for f in findings}
    assert "TODO" in patterns
    assert "pass\\b" in patterns
