from web_gui.scripts.flask_apps.enterprise_dashboard import app
from scripts.code_placeholder_audit import main


def test_dashboard_metrics_after_audit(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("# TODO\n")
    analytics = tmp_path / "analytics.db"
    dashboard_dir = tmp_path / "dashboard" / "compliance"

    main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dashboard_dir),
    )

    # patch dashboard constants
    import importlib

    dash = importlib.import_module("web_gui.scripts.flask_apps.enterprise_dashboard")
    monkeypatch.setattr(dash, "ANALYTICS_DB", analytics)
    monkeypatch.setattr(dash, "COMPLIANCE_DIR", dashboard_dir)

    client = app.test_client()
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()
    assert data["metrics"]["open_placeholders"] == 1
    assert data["metrics"]["total_placeholders"] == 1

    # remove placeholder and run in test mode
    target.write_text("def demo():\n    pass\n")
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dashboard_dir),
    )
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()
    assert data["metrics"]["placeholder_removal"] == 0
    assert data["metrics"]["open_placeholders"] == 1
    assert data["metrics"]["resolved_placeholders"] == 0
