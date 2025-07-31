#!/usr/bin/env python3
"""WebGUIIntegrationSystem - Enterprise Utility Script."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from web_gui.scripts.flask_apps.enterprise_dashboard import app
from web_gui.scripts.flask_apps.web_gui_integrator import WebGUIIntegrator
from utils.cross_platform_paths import CrossPlatformPathManager

__all__ = ["WebGUIIntegrationSystem", "main"]


class WebGUIIntegrationSystem:
    """Integrate the enterprise dashboard with database metrics."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        workspace = CrossPlatformPathManager.get_workspace_path()
        self.db_path = Path(db_path) if db_path else workspace / "databases" / "analytics.db"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.integrator = WebGUIIntegrator(self.db_path)

    def start(self, port: int = 5000) -> None:
        """Register endpoints and run the Flask app."""
        self.integrator.register_endpoints(app)
        self.integrator.initialize()
        self.logger.info("Starting dashboard on port %s", port)
        app.run(port=port)


def main() -> int:
    system = WebGUIIntegrationSystem()
    system.start()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
