import pytest

from src.dashboard import auth


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
