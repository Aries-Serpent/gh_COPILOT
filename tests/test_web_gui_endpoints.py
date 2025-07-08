import importlib
import pathlib


def _create_app():
    module = importlib.import_module(
        'web_gui.scripts.flask_apps.enterprise_dashboard')
    return module.app


def test_endpoints_available():
    app = _create_app()
    client = app.test_client()
    endpoints = ['/', '/database', '/api/scripts', '/backup',
                 '/migration', '/deployment', '/api/health']
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code in (200, 302)
