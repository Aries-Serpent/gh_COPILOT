import os
from scripts.enterprise.enterprise_api_infrastructure_framework import EnterpriseAuthentication

def test_secret_loaded_from_env(monkeypatch):
    monkeypatch.setenv("API_SECRET_KEY", "test_secret")
    auth = EnterpriseAuthentication(workspace_path=".")
    assert auth.secret_key == "test_secret"
