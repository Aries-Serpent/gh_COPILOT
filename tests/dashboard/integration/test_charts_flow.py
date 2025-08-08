from dashboard import enterprise_dashboard as ed
import dashboard.integrated_dashboard as idash


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(idash, "_load_metrics", lambda: {"composite_score": 0.9})
    client = ed.app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["composite_score"] == 0.9
