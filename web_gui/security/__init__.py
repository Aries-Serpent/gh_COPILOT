"""Security subsystem integrating authentication and authorization."""

from flask import Flask

from . import authentication, authorization, encryption, audit_logging, quantum_security


def init_app(app: Flask) -> None:
    """Initialize all security components for *app*."""
    authentication.init_app(app)
    authorization.init_app(app)
    encryption.init_app(app)
    audit_logging.init_app(app)
    quantum_security.init_app(app)


__all__ = [
    "authentication",
    "authorization",
    "encryption",
    "audit_logging",
    "quantum_security",
    "init_app",
]
