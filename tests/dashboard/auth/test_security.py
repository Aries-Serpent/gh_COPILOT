import pytest

from src.dashboard import auth


@pytest.fixture()
def manager():
    auth._RATE_LIMIT.clear()
    return auth.SessionManager.create()


def test_verify_token_and_session(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    session = manager.start_session("secret", "")
    assert auth.verify_token_and_session("secret", session, manager)
    assert not auth.verify_token_and_session("wrong", session, manager)
    assert not auth.verify_token_and_session("secret", "bad", manager)


def test_rate_limit(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    for _ in range(5):
        manager.start_session("secret", "")
    with pytest.raises(ValueError):
        manager.start_session("secret", "")


def test_refresh_invalid_session(monkeypatch, manager):
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    with pytest.raises(ValueError):
        manager.refresh_session("secret", "does-not-exist")
