import importlib
import json
import sqlite3


def test_compliance_metrics_updater(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1)")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (0.9)")
        conn.execute("CREATE TABLE violation_logs (id INTEGER)")
        conn.execute("INSERT INTO violation_logs VALUES (1)")
        conn.execute("CREATE TABLE rollback_logs (id INTEGER)")
        conn.execute("INSERT INTO rollback_logs VALUES (1)")

    dashboard_dir = tmp_path / "dashboard"
    updater = module.ComplianceMetricsUpdater(dashboard_dir)
    updater.update()
    assert updater.validate_update()

    metrics_file = dashboard_dir / "metrics.json"
    assert metrics_file.exists()
    data = json.loads(metrics_file.read_text())
    assert data["metrics"]["placeholder_removal"] == 1


def test_compliance_metrics_updater_simulate(tmp_path, monkeypatch):
    """Ensure simulate mode skips file creation."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1)")

    dashboard_dir = tmp_path / "dashboard"
    updater = module.ComplianceMetricsUpdater(dashboard_dir)
    updater.update(simulate=True)
    assert not (dashboard_dir / "metrics.json").exists()
