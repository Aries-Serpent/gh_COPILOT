import os
import sqlite3

from scripts.code_placeholder_audit import main as audit_main
from scripts.compliance.update_compliance_metrics import update_compliance_metrics


def test_audit_snapshot_used_by_compliance_metrics(tmp_path):
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    workspace = tmp_path
    (workspace / "databases").mkdir()
    (workspace / "dashboard" / "compliance").mkdir(parents=True)
    sample = workspace / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    analytics = workspace / "databases" / "analytics.db"
    production = workspace / "databases" / "production.db"
    audit_main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(production),
        dashboard_dir=str(workspace / "dashboard" / "compliance"),
        simulate=False,
    )
    update_compliance_metrics(str(workspace))
    with sqlite3.connect(analytics) as conn:
        open_count, resolved_count = conn.execute(
            "SELECT placeholders_open, placeholders_resolved FROM compliance_scores ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert open_count == 1
    assert resolved_count == 0
