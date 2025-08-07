"""Web GUI health check helpers.

This module verifies database connectivity and template rendering
for the web dashboard.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .performance_metrics import collect_performance_metrics
from .compliance_monitoring import check_compliance
from .quantum_metrics import quantum_metric
from .alerting.alert_manager import trigger_alert

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "production.db"
TEMPLATES_DIR = WORKSPACE_ROOT / "web_gui" / "templates"

__all__ = [
    "check_database_connection",
    "check_template_rendering",
    "check_system_resources",
    "check_compliance_status",
    "check_quantum_score",
    "run_all_checks",
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


def run_all_checks(
    compliance_data: Optional[Dict[str, str]] = None,
    quantum_values: Optional[Iterable[float]] = None,
    quantum_threshold: float = 0.0,
    alert: bool = False,
    notifier: Optional[Callable[[str], None]] = None,
    dashboard_router: Optional[Callable[[str, str], None]] = None,
) -> Dict[str, bool]:
    """Run available health checks and optionally trigger alerts.

    Parameters
    ----------
    compliance_data:
        Optional mapping to validate via :func:`check_compliance_status`.
    quantum_values:
        Optional collection passed to :func:`check_quantum_score`.
    quantum_threshold:
        Threshold forwarded to :func:`check_quantum_score` when values are provided.
    alert:
        When ``True`` an alert is emitted for any failing check using
        :func:`alerting.alert_manager.trigger_alert`.
    notifier:
        Optional callback used by :func:`trigger_alert` to deliver messages.
    dashboard_router:
        Optional callback used by :func:`trigger_alert` to route messages
        to dashboards.
    """

    results = {
        "database": check_database_connection(),
        "templates": check_template_rendering(),
        "resources": check_system_resources(),
    }
    if compliance_data is not None:
        results["compliance"] = check_compliance_status(compliance_data)
    if quantum_values is not None:
        results["quantum"] = check_quantum_score(quantum_values, quantum_threshold)

    if alert:
        for name, passed in results.items():
            if not passed:
                if notifier is not None:
                    trigger_alert(
                        f"{name} check failed", "critical", notifier, dashboard_router
                    )
                else:
                    trigger_alert(
                        f"{name} check failed", "critical", dashboard_router=dashboard_router
                    )

    return results
