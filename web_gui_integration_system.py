#!/usr/bin/env python3
"""Unified Web GUI Integration System.

This module provides a high-level interface that wraps existing Web-GUI
components into a single integration point. It consolidates the Flask
dashboard application, template management, and database connectivity.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader
from werkzeug.serving import make_server

from web_gui.scripts.flask_apps.enterprise_dashboard import \
    app as dashboard_app


@dataclass
class WebGUIConfig:
    """Configuration for Web GUI integration."""

    workspace_root: Path
    database_path: Path
    templates_path: Path


class WebGUIIntegrationSystem:
    """Scaffolding for a unified Web-GUI integration layer."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.config = WebGUIConfig(
            workspace_root=Path(workspace_root or "."),
            database_path=Path(workspace_root or ".") /
            "databases" / "production.db",
            templates_path=Path(workspace_root or ".") /
            "web_gui" / "templates",
        )
        self.dashboard_app = dashboard_app
        self.template_env = Environment(
            loader=FileSystemLoader(self.config.templates_path)
        )
        self.db_conn = sqlite3.connect(self.config.database_path)
        self._server = None
        self._server_thread = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all Web-GUI components in a unified manner."""
        port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
        self._server = make_server("127.0.0.1", port, self.dashboard_app)
        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )
        self._server_thread.start()
        self._initialized = True

    def status(self) -> Dict[str, Any]:
        """Return current status of the integration system."""
        return {
            "initialized": self._initialized,
            "workspace_root": str(self.config.workspace_root),
            "database": str(self.config.database_path),
            "templates": str(self.config.templates_path),
        }

    def shutdown(self) -> None:
        """Stop the dashboard server and close resources."""
        if self._server:
            self._server.shutdown()
        if self._server_thread:
            self._server_thread.join(timeout=5)
        if self.db_conn:
            self.db_conn.close()
        self._initialized = False


if __name__ == "__main__":
    system = WebGUIIntegrationSystem()
    system.initialize()
    print(system.status())
