"""Thin wrapper for the enterprise Flask app."""

from web_gui.scripts.flask_apps.enterprise_dashboard import app

__all__ = ["app", "main"]


def main() -> None:
    app.run(host="0.0.0.0", port=5000, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":
    main()

