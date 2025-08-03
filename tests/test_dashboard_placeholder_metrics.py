def test_dashboard_metrics_after_audit(monkeypatch):
    class DummyUpdater:
        def __init__(self, *args, **kwargs):
            pass

        def _fetch_compliance_metrics(self, *args, **kwargs):
            return {}

    monkeypatch.setattr(
        "dashboard.compliance_metrics_updater.ComplianceMetricsUpdater",
        DummyUpdater,
    )
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed

    sample_metrics = {
        "open_placeholders": 1,
        "total_placeholders": 1,
        "rollback_count": 0,
        "progress_status": "pending",
        "placeholder_removal": 0,
        "compliance_score": 1.0,
        "lessons_integration_status": "OK",
        "average_query_latency": 0.0,
        "placeholder_breakdown": {},
        "compliance_trend": [],
    }
    monkeypatch.setattr(ed, "_fetch_metrics", lambda: sample_metrics)
    monkeypatch.setattr(ed, "_fetch_rollbacks", lambda: [])

    client = ed.app.test_client()
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()
    assert data["metrics"]["open_placeholders"] == 1
    assert data["metrics"]["total_placeholders"] == 1
    assert "rollback_count" in data["metrics"]
    assert "progress_status" in data["metrics"]


def test_lessons_status_from_populated_db(tmp_path, monkeypatch):
    import sqlite3

    class DummyUpdater:
        def __init__(self, *args, **kwargs):
            pass

        def _fetch_compliance_metrics(self, *args, **kwargs):
            return {}

    monkeypatch.setattr(
        "dashboard.compliance_metrics_updater.ComplianceMetricsUpdater",
        DummyUpdater,
    )

    from web_gui.scripts.flask_apps import enterprise_dashboard as ed
    from dashboard import compliance_metrics_updater as cmu

    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE integration_score_calculations (integration_status TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO integration_score_calculations VALUES ('FULLY_INTEGRATED', '2024')"
        )
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'ok')")
        conn.execute(
            "CREATE TABLE performance_metrics (metric_name TEXT, metric_value REAL, metric_type TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO performance_metrics VALUES ('query_latency', 1.0, 'ms', '2024')"
        )

    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(ed, "metrics_updater", cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True))

    metrics = ed._fetch_metrics()
    assert metrics["lessons_integration_status"] == "FULLY_INTEGRATED"
