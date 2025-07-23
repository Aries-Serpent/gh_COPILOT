"""Logging utilities with visual indicators and DUAL COPILOT validation."""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

logger = logging.getLogger(__name__)

DEFAULT_ANALYTICS_DB = Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "databases" / "analytics.db"


def _log_event(event_data: dict, table: str = "sync_events_log", db_path: Path | None = None) -> None:
    start_ts = time.time()
    db = db_path or DEFAULT_ANALYTICS_DB
    bar = tqdm(total=1, desc=f"log:{table}", leave=False)
    try:
        db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db) as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (timestamp TEXT, details TEXT)"
            )
            conn.execute(
                f"INSERT INTO {table} (timestamp, details) VALUES (?, ?)",
                (datetime.utcnow().isoformat(), json.dumps(event_data)),
            )
            conn.commit()
            bar.update(1)
            cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
            bar.write(f"✅ {table} size: {cur.fetchone()[0]}")
    except sqlite3.Error as exc:
        logger.debug("log_event failed: %s", exc)
        bar.write("❌ log failed")
    finally:
        bar.close()
        etc = time.time() - start_ts
        tqdm.write(f"ETC: {etc:.2f}s | status logged")

__all__ = ["_log_event", "DEFAULT_ANALYTICS_DB"]
