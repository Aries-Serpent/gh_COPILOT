"""Logging utilities for gh_COPILOT Enterprise Toolkit"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_enterprise_logging(level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Setup enterprise-grade logging configuration"""

    if log_file is None:
        workspace = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
        log_dir = Path(workspace) / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
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
