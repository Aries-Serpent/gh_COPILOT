"""Web GUI health check helpers.

This module verifies database connectivity and template rendering
for the web dashboard.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .performance_metrics import collect_performance_metrics
from .compliance_monitoring import check_compliance
from .quantum_metrics import quantum_metric

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "production.db"
TEMPLATES_DIR = WORKSPACE_ROOT / "web_gui" / "templates"

__all__ = [
    "check_database_connection",
    "check_template_rendering",
    "check_system_resources",
    "check_compliance_status",
    "check_quantum_score",
]


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


def check_system_resources(
    cpu_threshold: float = 90.0, mem_threshold: float = 90.0
) -> bool:
    """Return ``True`` if system resource usage is below thresholds."""
    metrics = collect_performance_metrics()
    return (
        metrics.get("cpu_percent", 0.0) < cpu_threshold
        and metrics.get("memory_percent", 0.0) < mem_threshold
    )


def check_compliance_status(data: Dict[str, str]) -> bool:
    """Proxy to :func:`check_compliance` for convenience."""
    return check_compliance(data)


def check_quantum_score(values: Iterable[float], threshold: float = 0.0) -> bool:
    """Return ``True`` if the quantum score meets ``threshold``."""
    return quantum_metric(values) >= threshold
