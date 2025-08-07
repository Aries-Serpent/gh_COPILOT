from web_gui.scripts.config.development_config import DevelopmentConfig
from web_gui.scripts.config.production_config import ProductionConfig
from web_gui.scripts.config.staging_config import StagingConfig


def test_production_config_defaults_secure() -> None:
    cfg = ProductionConfig()
    assert not cfg.DEBUG
    assert cfg.SESSION_COOKIE_SECURE
    assert cfg.WTF_CSRF_ENABLED


def test_development_config_defaults_relaxed() -> None:
    cfg = DevelopmentConfig()
    assert cfg.DEBUG
    assert not cfg.SESSION_COOKIE_SECURE
    assert not cfg.WTF_CSRF_ENABLED


def test_staging_config_defaults_balanced() -> None:
    cfg = StagingConfig()
    assert not cfg.DEBUG
    assert cfg.WTF_CSRF_ENABLED
    assert not cfg.SESSION_COOKIE_SECURE
