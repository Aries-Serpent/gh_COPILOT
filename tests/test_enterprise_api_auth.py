import pytest
from scripts.enterprise.enterprise_api_infrastructure_framework import EnterpriseAuthentication

def test_secret_loaded_from_env(monkeypatch):
    monkeypatch.setenv("API_SECRET_KEY", "test_secret")
    auth = EnterpriseAuthentication(workspace_path=".")
    assert auth.secret_key == "test_secret"


def test_missing_secret_exits(monkeypatch):
    monkeypatch.delenv("API_SECRET_KEY", raising=False)
    with pytest.raises(SystemExit):
        EnterpriseAuthentication(workspace_path=".")
