"""Web GUI health check helpers.

This module verifies database connectivity and template rendering
for the web dashboard.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, MutableMapping, Optional

try:  # pragma: no cover - psutil optional
    import psutil  # type: ignore
except ImportError:  # pragma: no cover - fallback
    psutil = None  # type: ignore[assignment]
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from secondary_copilot_validator import SecondaryCopilotValidator

from .performance_metrics import collect_performance_metrics
from .compliance_monitoring import check_compliance
from .quantum_metrics import quantum_metric
from .alerting.alert_manager import trigger_alert

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "production.db"
TEMPLATES_DIR = WORKSPACE_ROOT / "web_gui" / "templates"

logger = logging.getLogger(__name__)

__all__ = [
    "check_database_connection",
    "check_template_rendering",
    "check_system_resources",
    "check_cache_status",
    "get_service_uptime",
    "check_compliance_status",
    "check_quantum_score",
    "run_all_checks",
]


def check_database_connection(
    db_path: Optional[Path] = None,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if a connection to the database can be established."""
    validator = validator or SecondaryCopilotValidator()
    path = db_path or DB_PATH
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("SELECT 1")
        logger.info("Database connectivity check passed")
        result = True
    except sqlite3.Error as exc:
        logger.error("Database connectivity check failed: %s", exc)
        result = False
    validator.validate_corrections([str(result)])
    return result


def check_template_rendering(
    template_name: str = "dashboard.html",
    templates_dir: Optional[Path] = None,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if the template can be loaded and rendered."""
    validator = validator or SecondaryCopilotValidator()
    directory = templates_dir or TEMPLATES_DIR
    env = Environment(loader=FileSystemLoader(str(directory)))
    try:
        template = env.get_template(template_name)
        template.render(url_for=lambda *args, **kwargs: "", metrics={})
        logger.info("Template %s rendered successfully", template_name)
        result = True
    except (TemplateNotFound, OSError) as exc:
        logger.error("Template rendering failed: %s", exc)
        result = False
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Template rendering error: %s", exc)
        result = False
    validator.validate_corrections([str(result)])
    return result


def check_system_resources(
    cpu_threshold: float = 90.0,
    mem_threshold: float = 90.0,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if system resource usage is below thresholds."""
    validator = validator or SecondaryCopilotValidator()
    metrics = collect_performance_metrics()
    result = (
        metrics.get("cpu_percent", 0.0) < cpu_threshold
        and metrics.get("memory_percent", 0.0) < mem_threshold
    )
    logger.info("System resources within thresholds: %s", result)
    validator.validate_corrections([str(result)])
    return result


def check_cache_status(
    cache: MutableMapping[str, object] | None = None,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if *cache* is available and writable."""
    validator = validator or SecondaryCopilotValidator()
    healthy = False
    if cache is not None:
        try:
            cache["__health_check__"] = "ok"
            healthy = cache.get("__health_check__") == "ok"
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Cache check failed: %s", exc)
            healthy = False
    logger.info("Cache status healthy: %s", healthy)
    validator.validate_corrections([str(healthy)])
    return healthy


def get_service_uptime(
    validator: SecondaryCopilotValidator | None = None,
) -> float:
    """Return system uptime in seconds."""
    validator = validator or SecondaryCopilotValidator()
    if psutil is None:
        logger.warning("psutil not installed; uptime unavailable")
        uptime = 0.0
    else:
        uptime = time.time() - psutil.boot_time()
    logger.info("Service uptime: %s", uptime)
    validator.validate_corrections([str(uptime)])
    return uptime


def check_compliance_status(
    data: Dict[str, str],
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Proxy to :func:`check_compliance` for convenience."""
    validator = validator or SecondaryCopilotValidator()
    result = check_compliance(data)
    logger.info("Compliance status: %s", result)
    validator.validate_corrections([str(result)])
    return result


def check_quantum_score(
    values: Iterable[float],
    threshold: float = 0.0,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if the quantum score meets ``threshold``."""
    validator = validator or SecondaryCopilotValidator()
    result = quantum_metric(values) >= threshold
    logger.info("Quantum score meets threshold %s: %s", threshold, result)
    validator.validate_corrections([str(result)])
    return result


def run_all_checks(
    compliance_data: Optional[Dict[str, str]] = None,
    quantum_values: Optional[Iterable[float]] = None,
    quantum_threshold: float = 0.0,
    cache: MutableMapping[str, object] | None = None,
    alert: bool = False,
    notifier: Optional[Callable[[str], None]] = None,
    dashboard_router: Optional[Callable[[str, str], None]] = None,
    validator: SecondaryCopilotValidator | None = None,
) -> Dict[str, bool | float]:
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
    pipeline:
        Optional iterable of alert handlers forwarded to
        :func:`~web_gui.monitoring.alerting.alert_manager.trigger_alert`.
    """

    validator = validator or SecondaryCopilotValidator()

    results = {
        "database": check_database_connection(validator=validator),
        "templates": check_template_rendering(validator=validator),
        "resources": check_system_resources(validator=validator),
        "cache": check_cache_status(cache, validator=validator),
        "uptime": get_service_uptime(validator=validator),
    }
    if compliance_data is not None:
        results["compliance"] = check_compliance_status(
            compliance_data, validator=validator
        )
    if quantum_values is not None:
        results["quantum"] = check_quantum_score(
            quantum_values, quantum_threshold, validator=validator
        )
    pipeline_handlers: list[Callable[[str, str], None]] | None = None
    if notifier or dashboard_router:
        pipeline_handlers = []
        if notifier is not None:
            pipeline_handlers.append(
                lambda lvl, msg: notifier(f"[{lvl.upper()}] {msg}")
            )
        if dashboard_router is not None:
            pipeline_handlers.append(dashboard_router)

    if alert:
        for name, passed in results.items():
            if not passed:
                trigger_alert(
                    f"{name} check failed", "critical", pipeline=pipeline_handlers
                )

    logger.debug("Health check results: %s", results)
    validator.validate_corrections([str(results)])
    return results
