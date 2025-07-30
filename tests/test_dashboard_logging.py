from dashboard import compliance_metrics_updater as cmu


def test_dashboard_update_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    events = []
    monkeypatch.setattr(
        cmu.ComplianceMetricsUpdater,
        "_log_update_event",
        lambda self, metrics, **k: events.append({"event": "dashboard_update"}),
    )
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "analytics.db").touch()
    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash, test_mode=True)
    monkeypatch.setattr(updater, "_check_forbidden_operations", lambda: None)
    updater._fetch_compliance_metrics = lambda **k: {}
    updater.update()
    assert any(e.get("event") == "dashboard_update" for e in events)
