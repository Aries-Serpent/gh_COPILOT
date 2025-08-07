from web_gui.scripts.config.production_config import ProductionConfig


def test_production_config_defaults_secure() -> None:
    cfg = ProductionConfig()
    assert not cfg.DEBUG
    assert cfg.SESSION_COOKIE_SECURE
    assert cfg.WTF_CSRF_ENABLED
