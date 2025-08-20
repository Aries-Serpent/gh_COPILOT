"""Flask route blueprints for dashboard."""

from __future__ import annotations

from flask import Flask

from .corrections import bp as corrections_bp
from .compliance import bp as compliance_bp
from .rollbacks import bp as rollbacks_bp


def register_routes(app: Flask) -> None:
    """Register dashboard blueprints on the given Flask app."""
    app.register_blueprint(corrections_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(rollbacks_bp)


__all__ = ["register_routes", "corrections_bp", "compliance_bp", "rollbacks_bp"]

