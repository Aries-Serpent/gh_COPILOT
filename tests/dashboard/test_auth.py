import pytest

pytest.importorskip("pyotp")
import pyotp

from src.dashboard import auth


@pytest.fixture()
def manager():
    return auth.SessionManager.create()


def _otp(secret: str) -> str:
    return pyotp.TOTP(secret).now()


def test_successful_auth_flow(monkeypatch, manager):
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    session = manager.start_session("secret", _otp(secret))
    assert manager.validate("secret", session)
    manager.end_session(session)
    assert not manager.validate("secret", session)


def test_failed_auth_flow(monkeypatch, manager):
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    with pytest.raises(ValueError):
        manager.start_session("bad", _otp(secret))
    assert not manager.validate("bad", "none")
    with pytest.raises(ValueError):
        manager.start_session("secret", "000000")
    session = manager.start_session("secret", _otp(secret))
    assert not manager.validate("secret", "wrong")


def test_session_refresh_and_expiry(monkeypatch, manager):
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    session = manager.start_session("secret", _otp(secret))
    new_session = manager.refresh_session("secret", session)
    assert new_session != session
    assert not manager.validate("secret", session)
    assert manager.validate("secret", new_session)
    now = auth.time.time()
    monkeypatch.setattr(auth.time, "time", lambda: now + manager.session_timeout + 1)
    assert not manager.validate("secret", new_session)
