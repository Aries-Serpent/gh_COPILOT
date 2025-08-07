"""Certificate utilities for the web GUI."""

from flask import Flask

from .ssl_config import create_ssl_context


def init_app(app: Flask) -> None:
    """Configure an SSL context if certificate paths are provided."""
    cert = app.config.get("SSL_CERT_FILE")
    key = app.config.get("SSL_KEY_FILE")
    ca = app.config.get("SSL_CA_FILE")
    if cert and key:
        app.config["SSL_CONTEXT"] = create_ssl_context(cert, key, ca)


__all__ = ["init_app", "create_ssl_context"]
