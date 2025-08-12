import pytest

from src.dashboard import auth


@pytest.fixture(autouse=True)
def _mock_mfa(monkeypatch):
    monkeypatch.setattr(auth, "_check_mfa", lambda *_: None)


@pytest.fixture()
def manager():
    return auth.SessionManager.create()


def test_successful_auth_flow(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    session = manager.start_session("secret")
    assert manager.validate("secret", session)
    manager.end_session(session)
    assert not manager.validate("secret", session)


def test_failed_auth_flow(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    with pytest.raises(ValueError):
        manager.start_session("bad")
    assert not manager.validate("bad", "none")
    session = manager.start_session("secret")
    assert not manager.validate("secret", "wrong")


def test_session_refresh_and_expiry(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    session = manager.start_session("secret")
    new_session = manager.refresh_session("secret", session)
    assert new_session != session
    assert not manager.validate("secret", session)
    assert manager.validate("secret", new_session)
    now = auth.time.time()
    monkeypatch.setattr(auth.time, "time", lambda: now + manager.session_timeout + 1)
    assert not manager.validate("secret", new_session)
