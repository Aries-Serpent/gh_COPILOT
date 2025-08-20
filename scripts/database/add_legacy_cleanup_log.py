from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from scripts.database.size_compliance_checker import check_database_sizes
from utils.log_utils import _log_event

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS legacy_cleanup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_legacy_cleanup_log_timestamp
    ON legacy_cleanup_log(timestamp);
"""



def add_table(db_path: Path) -> None:
    """Create ``legacy_cleanup_log`` table in ``db_path``."""
    start_time = datetime.now()
    logger.info("[START] add_table for %s", db_path)
    logger.info("Process ID: %s", os.getpid())

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(total=1, desc="create-table", unit="step") as bar:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        bar.update(1)
    logger.info("legacy_cleanup_log ensured in %s", db_path)
    check_database_sizes(db_path.parent)
    _log_event({"event": "legacy_cleanup_log_ready", "db": str(db_path)})

    elapsed = datetime.now() - start_time
    logger.info("[SUCCESS] Completed in %s", str(elapsed))



def ensure_legacy_cleanup_log(db_path: Path) -> None:
    """Ensure ``legacy_cleanup_log`` table exists."""
    add_table(db_path)



def log_cleanup_event(file_path: str, action: str, reason: str, *, db_path: Path) -> None:
    """Record a cleanup event to ``legacy_cleanup_log``."""
    entry = {
        "file": file_path,
        "action": action,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    _log_event(entry, table="legacy_cleanup_log", db_path=db_path)



def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "analytics.db"
    start = datetime.now()
    add_table(db_path)
    etc = start + timedelta(seconds=1)
    logger.info(
        "Migration completed at %s | ETC was %s",
        datetime.utcnow().isoformat(),
        etc.strftime("%Y-%m-%d %H:%M:%S"),
    )


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    main()

__all__ = ["add_table", "ensure_legacy_cleanup_log", "log_cleanup_event"]
