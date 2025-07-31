from config.secret_manager import get_secret


def test_get_secret_found(monkeypatch):
    monkeypatch.setenv("SECRET_TEST", "value")
    assert get_secret("SECRET_TEST") == "value"


def test_get_secret_default(monkeypatch):
    monkeypatch.delenv("SECRET_TEST", raising=False)
    assert get_secret("SECRET_TEST", "default") == "default"

