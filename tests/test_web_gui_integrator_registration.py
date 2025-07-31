import shutil
from pathlib import Path

from web_gui.scripts.flask_apps.enterprise_dashboard import app
from web_gui.scripts.flask_apps.web_gui_integrator import WebGUIIntegrator


def test_integrator_registers_endpoints(tmp_path, monkeypatch):
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
    ]
    for path in paths:
        resp = client.get(path)
        assert resp.status_code == 200
