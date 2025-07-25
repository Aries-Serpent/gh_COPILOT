"""Start the enterprise Flask dashboard.

This wrapper loads ``app`` from :mod:`web_gui.scripts.flask_apps.enterprise_dashboard`
and exposes a ``main`` entry point for command-line execution. The dashboard
listens on ``FLASK_RUN_PORT`` when set, falling back to port ``5000``.
"""

from __future__ import annotations

import os

from web_gui.scripts.flask_apps.enterprise_dashboard import app

__all__ = ["app", "main"]


def main() -> None:
    """Run the wrapped Flask app."""
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":
    main()
