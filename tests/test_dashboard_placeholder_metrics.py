def test_dashboard_metrics_after_audit(monkeypatch):
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
