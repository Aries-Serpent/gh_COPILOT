import importlib


def test_audit_triggers_compliance_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "mod.py").write_text("pass  # TODO\n", encoding="utf-8")
    analytics = tmp_path / "analytics.db"
    dash = tmp_path / "dashboard"

    calls = []

    class StubUpdater:
        def __init__(self, dashboard_dir, test_mode=False):
            self.dashboard_dir = dashboard_dir
            self.test_mode = test_mode

        def update(self, simulate=False):
            calls.append(simulate)

        def validate_update(self):
            return True

    module = importlib.import_module("scripts.code_placeholder_audit")
    monkeypatch.setattr(module, "ComplianceMetricsUpdater", StubUpdater)

    module.main(
        workspace_path=str(ws),
        analytics_db=str(analytics),
        dashboard_dir=str(dash),
        simulate=True,
    )

    assert calls == [True]
