import json
import sqlite3

from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
from scripts.code_placeholder_audit import main


def test_placeholder_removal_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("# TODO placeholder\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

    monkeypatch.setattr("dashboard.compliance_metrics_updater.ANALYTICS_DB", analytics)

    monkeypatch.setattr(ComplianceMetricsUpdater, "_check_forbidden_operations", lambda self: None)
    monkeypatch.setattr("dashboard.compliance_metrics_updater.validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr("dashboard.compliance_metrics_updater.validate_environment_root", lambda: None)
    monkeypatch.setattr(ComplianceMetricsUpdater, "_log_update_event", lambda self, metrics, test_mode=False: None)
    monkeypatch.setattr(ComplianceMetricsUpdater, "_update_dashboard", lambda self, metrics: None)
    monkeypatch.setattr("dashboard.compliance_metrics_updater.ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr("dashboard.compliance_metrics_updater.insert_event", lambda *a, **k: None)
    monkeypatch.setattr("utils.log_utils.insert_event", lambda *a, **k: -1)

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        apply_fixes=True,
    )

    with sqlite3.connect(analytics) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='resolved'")
        resolved = cur.fetchone()[0]
        conn.execute("CREATE TABLE IF NOT EXISTS correction_history (fix_applied TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS correction_logs (compliance_score REAL)")

    summary = dash_dir / "compliance" / "placeholder_summary.json"
    assert summary.exists()
    data = json.loads(summary.read_text())
    assert "resolved_count" in data
