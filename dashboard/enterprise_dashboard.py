"""Expose the enterprise Flask app for external use."""

from web_gui.scripts.flask_apps.enterprise_dashboard import app

__all__ = ["app"]
