import os
import pytest

from scripts.enterprise.enterprise_api_infrastructure_framework import EnterpriseAPIServer


def test_debug_disabled_in_production(monkeypatch):
    monkeypatch.setenv("API_SECRET_KEY", "secret")
    monkeypatch.setenv("FLASK_ENV", "production")
    server = EnterpriseAPIServer(workspace_path=".")
    assert server.debug is False


def test_cors_rejects_unauthorized_origin(monkeypatch):
    monkeypatch.setenv("API_SECRET_KEY", "secret")
    monkeypatch.setenv("API_ALLOWED_ORIGINS", "http://allowed.com")
    server = EnterpriseAPIServer(workspace_path=".")
    if server.app is None:
        pytest.skip("Flask not available")
    client = server.app.test_client()
    resp = client.get("/api/v1/health", headers={"Origin": "http://evil.com"})
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") is None
