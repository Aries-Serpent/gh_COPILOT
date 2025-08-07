"""Web GUI health check helpers.

This module verifies database connectivity and template rendering
for the web dashboard.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "production.db"
TEMPLATES_DIR = WORKSPACE_ROOT / "web_gui" / "templates"

__all__ = ["check_database_connection", "check_template_rendering"]


def check_database_connection(db_path: Optional[Path] = None) -> bool:
    """Return ``True`` if a connection to the database can be established."""
    path = db_path or DB_PATH
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def check_template_rendering(
    template_name: str = "dashboard.html",
    templates_dir: Optional[Path] = None,
) -> bool:
    """Return ``True`` if the template can be loaded and rendered."""
    directory = templates_dir or TEMPLATES_DIR
    env = Environment(loader=FileSystemLoader(str(directory)))
    try:
        template = env.get_template(template_name)
        template.render(url_for=lambda *args, **kwargs: "", metrics={})
        return True
    except (TemplateNotFound, OSError):
        return False
    except Exception:
        return False
