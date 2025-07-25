"""Wrapper for the Flask app defined in :mod:`web_gui.scripts.flask_apps.enterprise_dashboard`."""
from web_gui.scripts.flask_apps.enterprise_dashboard import app

__all__ = ["app"]

if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000)
