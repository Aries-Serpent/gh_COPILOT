import shutil
from pathlib import Path

from web_gui.scripts.flask_apps.web_gui_integrator import WebGUIIntegrator


def test_integrator_registers_endpoints(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps.enterprise_dashboard import app

    db_copy = tmp_path / "production.db"
    shutil.copy(Path("databases/production.db"), db_copy)
    monkeypatch.setenv("ENTERPRISE_AUTH_DISABLED", "1")
    integrator = WebGUIIntegrator(db_copy)
    integrator.register_endpoints(app)

    client = app.test_client()
    paths = [
        "/",
        "/database",
        "/backup",
        "/migration",
        "/deployment",
        "/api/scripts",
        "/api/health",
        "/api/compliance",
        "/api/rollbacks",
        "/api/corrections",
    ]
    for path in paths:
        resp = client.get(path)
        assert resp.status_code == 200

    stream_resp = client.get("/api/compliance_stream?once=1")
    assert stream_resp.status_code == 200

    post_paths = ["/api/ingest", "/api/rollback", "/api/backup"]
    for path in post_paths:
        resp = client.post(path, json={})
        assert resp.status_code == 200
