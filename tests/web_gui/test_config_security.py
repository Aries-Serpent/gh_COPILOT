import os
from typing import Generator

import pytest

from web_gui.scripts.config.production_config import ProductionConfig


@pytest.fixture(autouse=True)
def clear_env() -> Generator[None, None, None]:
    """Ensure environment is clean for each test."""
    original = os.environ.copy()
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_production_config_defaults_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLASK_SECRET_KEY", "x" * 32)
    cfg = ProductionConfig()
    assert not cfg.DEBUG
    assert cfg.SESSION_COOKIE_SECURE
    assert cfg.WTF_CSRF_ENABLED
    assert cfg.MAX_CONTENT_LENGTH == 1_048_576


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLASK_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("WEB_GUI_MAX_CONTENT_LENGTH", "2048")
    cfg = ProductionConfig()
    assert cfg.MAX_CONTENT_LENGTH == 2048


def test_missing_secret_key_raises() -> None:
    with pytest.raises(ValueError):
        ProductionConfig()


def test_insecure_cookie_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLASK_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("WEB_GUI_SESSION_COOKIE_SECURE", "0")
    with pytest.raises(ValueError):
        ProductionConfig()
