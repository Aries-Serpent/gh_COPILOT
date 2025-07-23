"""Logging utilities for gh_COPILOT Enterprise Toolkit"""

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def setup_enterprise_logging(
    level: str = "INFO", log_file: str = None
) -> logging.Logger:
    """Setup enterprise-grade logging configuration"""

    if log_file is None:
        workspace = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
        log_dir = Path(workspace) / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    return logging.getLogger("gh_COPILOT")


def log_enterprise_operation(operation: str, status: str, details: str = "") -> None:
    """Log enterprise operation with standard format"""
    logger = logging.getLogger("gh_COPILOT")

    if status.upper() == "SUCCESS":
        logger.info(f"✅ {operation}: {details}")
    elif status.upper() == "WARNING":
        logger.warning(f"⚠️ {operation}: {details}")
    elif status.upper() == "ERROR":
        logger.error(f"❌ {operation}: {details}")
    else:
        logger.info(f"📊 {operation}: {details}")


ANALYTICS_DB = Path("databases") / "analytics.db"


def _log_event(
    event: str,
    details: str,
    *,
    table: str = "sync_events_log",
    analytics_db: Path = ANALYTICS_DB,
) -> None:
    """Log synchronization or status events to ``analytics_db``."""
    try:
        analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(analytics_db) as conn:
            if table == "sync_status":
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS sync_status (timestamp TEXT, event TEXT, status TEXT)"
                )
                conn.execute(
                    "INSERT INTO sync_status (timestamp, event, status) VALUES (?, ?, ?)",
                    (datetime.utcnow().isoformat(), event, details),
                )
            else:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS sync_events_log (timestamp TEXT, event TEXT, details TEXT)"
                )
                conn.execute(
                    "INSERT INTO sync_events_log (timestamp, event, details) VALUES (?, ?, ?)",
                    (datetime.utcnow().isoformat(), event, details),
                )
            conn.commit()
    except sqlite3.Error as exc:
        logging.getLogger(__name__).debug("log_event failed: %s", exc)
