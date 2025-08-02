import pytest

from security.compliance_checker import enforce_security_policies


def test_enforce_security_policies(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    policy = tmp_path / "enterprise_security_policy.json"
    policy.write_text('{"encryption": "AES256", "access_control": "RBAC"}')
    enforce_security_policies(policy)


def test_enforce_security_policies_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    policy = tmp_path / "enterprise_security_policy.json"
    policy.write_text('{"encryption": "AES256"}')
    with pytest.raises(ValueError):
        enforce_security_policies(policy)
