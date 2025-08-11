import json
import sqlite3

from scripts import code_placeholder_audit as audit
from scripts.code_placeholder_audit import (
    log_findings,
    log_placeholder_tasks,
    snapshot_placeholder_counts,
    update_dashboard,
)


def test_log_findings_updates_tables(tmp_path):
    audit._snapshot_recorded = False
    db = tmp_path / "analytics.db"
    results = [
        {"file": "a.py", "line": 1, "pattern": "TODO", "context": "TODO item"},
        {"file": "b.py", "line": 2, "pattern": "FIXME", "context": "FIXME item"},
    ]
    inserted = log_findings(results, db, simulate=False)
    assert inserted == 2
    # record metrics and snapshot for placeholder counts
    log_placeholder_tasks([], db)
    open_count, resolved_count = snapshot_placeholder_counts(db)
    assert open_count == 2
    assert resolved_count == 0
    with sqlite3.connect(db) as conn:
        cur = conn.execute(
            "SELECT file_path, line_number, pattern, context, status FROM placeholder_tasks ORDER BY file_path"
        )
        rows = cur.fetchall()
        assert rows == [
            ("a.py", 1, "TODO", "TODO item", "open"),
            ("b.py", 2, "FIXME", "FIXME item", "open"),
        ]
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_audit_snapshots")
        assert cur.fetchone()[0] == 1


def test_update_dashboard_writes_counts_and_history(tmp_path):
    audit._snapshot_recorded = False
    db = tmp_path / "analytics.db"
    dash = tmp_path / "dashboard"
    results = [{"file": "c.py", "line": 3, "pattern": "BUG", "context": "bug"}]
    log_findings(results, db, simulate=False)
    snapshot_placeholder_counts(db)
    # metrics are recorded via log_placeholder_tasks
    log_placeholder_tasks([], db)
    update_dashboard(dash, db)
    counts = json.loads((dash / "placeholder_counts.json").read_text())
    assert counts["open"] == 1
    assert counts["resolved"] == 0
    history = json.loads((dash / "placeholder_history.json").read_text())
    assert history["history"] and history["history"][0]["open_count"] == 1
