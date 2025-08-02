from dashboard import compliance_metrics_updater as cmu


def test_dashboard_update_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    events = []
    
    def log_update_event(self, metrics, **k):  # noqa: ANN001, D401
        events.append({"event": "dashboard_update"})

    monkeypatch.setattr(
        cmu.ComplianceMetricsUpdater,
        "_log_update_event",
        log_update_event,
    )
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "analytics.db").touch()
    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash, test_mode=True)

    def noop(*a, **k):  # noqa: ANN001
        return None

    monkeypatch.setattr(updater, "_check_forbidden_operations", noop)

    def fetch_metrics(**k):  # noqa: ANN001
        return {}

    updater._fetch_compliance_metrics = fetch_metrics
    updater.update()
    assert any(e.get("event") == "dashboard_update" for e in events)
