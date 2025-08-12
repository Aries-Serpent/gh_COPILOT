import pytest

from src.dashboard import auth

pyotp = pytest.importorskip("pyotp")


@pytest.fixture()
def manager() -> auth.SessionManager:
    return auth.SessionManager.create()


def test_session_requires_valid_mfa(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    valid = pyotp.TOTP(secret).now()
    session = manager.start_session("secret", valid)
    assert manager.validate("secret", session)
    with pytest.raises(ValueError):
        manager.start_session("secret", "000000")


def test_start_session_without_mfa(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    with pytest.raises(ValueError):
        manager.start_session("secret")
