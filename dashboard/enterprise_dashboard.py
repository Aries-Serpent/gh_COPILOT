"""Start the enterprise Flask dashboard.

This wrapper loads ``app`` from :mod:`web_gui.scripts.flask_apps.enterprise_dashboard`
and exposes a ``main`` entry point for command-line execution. The dashboard
listens on ``FLASK_RUN_PORT`` when set, falling back to port ``5000``.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from web_gui.scripts.flask_apps.enterprise_dashboard import app
from utils.validation_utils import validate_enterprise_environment

__all__ = ["app", "main"]


def _validate_environment() -> None:
    """Validate required environment variables."""
    try:
        validate_enterprise_environment()
    except EnvironmentError as exc:
        logging.error("Environment validation failed: %s", exc)
        raise
    for var in ["GH_COPILOT_WORKSPACE", "GH_COPILOT_BACKUP_ROOT"]:
        logging.info("%s=%s", var, os.getenv(var))


def main() -> None:
    """Run the wrapped Flask app with startup logging."""
    logging.basicConfig(level=logging.INFO)
    logging.info("Dashboard starting at %s", datetime.utcnow().isoformat())
    _validate_environment()
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":
    main()
