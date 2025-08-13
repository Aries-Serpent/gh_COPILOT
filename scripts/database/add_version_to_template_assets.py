"""Add a version column to the ``template_assets`` table."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from .size_compliance_checker import check_database_sizes
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator
from utils.log_utils import _log_event

logger = logging.getLogger(__name__)

SCHEMA_SQL = "ALTER TABLE template_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1"


def add_column(db_path: Path) -> None:
    """Ensure ``template_assets`` has a ``version`` column."""
    start_time = datetime.now()
    logger.info("[START] add_column for %s", db_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn, tqdm(total=1, desc="add-column", unit="step") as bar:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(template_assets)")}
        if "version" not in columns:
            conn.execute(SCHEMA_SQL)
            conn.commit()
        bar.update(1)

    check_database_sizes(db_path.parent)
    _log_event({"event": "template_assets_version_ready", "db": str(db_path)})
    DualCopilotOrchestrator().validator.validate_corrections([str(db_path)])
    elapsed = datetime.now() - start_time
    etc = start_time + timedelta(seconds=1)
    logger.info("[SUCCESS] Completed in %s | ETC was %s", str(elapsed), etc.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root = Path(__file__).resolve().parents[1]
    db = root / "databases" / "enterprise_assets.db"
    add_column(db)

__all__ = ["add_column"]
