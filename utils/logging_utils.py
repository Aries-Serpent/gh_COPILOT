"""Logging utilities for gh_COPILOT Enterprise Toolkit"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager
from enterprise_modules.database_utils import (
    enterprise_database_context,
    execute_safe_insert,
    execute_safe_query,
)


def setup_enterprise_logging(level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Setup enterprise-grade logging configuration"""

    if log_file is None:
        workspace = CrossPlatformPathManager.get_workspace_path()
        log_dir = workspace / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file, delay=True), logging.StreamHandler()],
    )

    return logging.getLogger("gh_COPILOT")


def log_enterprise_operation(operation: str, status: str, details: str = "") -> None:
    """Log enterprise operation with standard format"""
    logger = logging.getLogger("gh_COPILOT")

    tag_map = {
        "SUCCESS": "[SUCCESS]",
        "WARNING": "[WARNING]",
        "ERROR": "[ERROR]",
        "INFO": "[INFO]",
    }
    prefix = tag_map.get(status.upper(), "[INFO]")

    if status.upper() == "ERROR":
        logger.error(f"{prefix} {operation}: {details}")
    elif status.upper() == "WARNING":
        logger.warning(f"{prefix} {operation}: {details}")
    else:
        logger.info(f"{prefix} {operation}: {details}")


def log_dual_validation_outcome(primary: object, secondary: object) -> None:
    """Record outcomes from each copilot and note discrepancies."""
    log_enterprise_operation("Primary copilot", "INFO", str(primary))
    log_enterprise_operation("Secondary copilot", "INFO", str(secondary))
    if primary != secondary:
        log_enterprise_operation(
            "Dual validation discrepancy",
            "WARNING",
            f"primary={primary} secondary={secondary}",
        )


ANALYTICS_DB = Path("databases") / "analytics.db"


def log_session_event(
    session_id: str,
    event: str,
    *,
    db_path: Path = ANALYTICS_DB,
) -> bool:
    """Record a session event in ``analytics.db``.

    Parameters
    ----------
    session_id:
        Identifier for the active session.
    event:
        Description of the event to record.
    db_path:
        Path to the analytics database. Defaults to :data:`ANALYTICS_DB`.

    Returns
    -------
    bool
        ``True`` if the insert succeeded, ``False`` otherwise.
    """
    timestamp = datetime.now(UTC).isoformat()
    with enterprise_database_context(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_history (
                session_id TEXT,
                event TEXT,
                timestamp TEXT
            )
            """
        )
        data = {"session_id": session_id, "event": event, "timestamp": timestamp}
        return execute_safe_insert(conn, "session_history", data)


def get_session_history(
    session_id: str,
    *,
    db_path: Path = ANALYTICS_DB,
) -> list:
    """Retrieve logged events for ``session_id`` ordered by timestamp."""
    with enterprise_database_context(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_history (
                session_id TEXT,
                event TEXT,
                timestamp TEXT
            )
            """
        )
        rows = execute_safe_query(
            conn,
            "SELECT event, timestamp FROM session_history WHERE session_id=? ORDER BY timestamp",
            (session_id,),
        )
        return [dict(r) for r in rows] if rows else []
