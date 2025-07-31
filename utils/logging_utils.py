"""Logging utilities for gh_COPILOT Enterprise Toolkit"""

import logging
from datetime import datetime
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager


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


ANALYTICS_DB = Path("databases") / "analytics.db"
