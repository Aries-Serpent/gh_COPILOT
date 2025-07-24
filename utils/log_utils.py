import json
import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

ANALYTICS_DB = Path("databases") / "analytics.db"
logger = logging.getLogger(__name__)
__all__ = ["_log_event"]


def _log_event(
    event_data: dict,
    *,
    table: str = "sync_events_log",
    db_path: Path = ANALYTICS_DB,
) -> bool:
    """Record an event in ``db_path`` under ``table`` with visual indicators."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    event_json = json.dumps(event_data)
    start_ts = time.time()
    try:
        with tqdm(total=1, desc="log", unit="evt", leave=False) as bar:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    f"CREATE TABLE IF NOT EXISTS {table} (timestamp TEXT, data TEXT)"
                )
                conn.execute(
                    f"INSERT INTO {table} (timestamp, data) VALUES (?, ?)",
                    (datetime.now(timezone.utc).isoformat(), event_json),
                )
                conn.commit()
            bar.update(1)
            bar.set_postfix_str("ETC: 0s")
        duration = time.time() - start_ts
        logger.info("Logged event to %s: %s | %.2fs", table, event_json, duration)
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE data=?",
                (event_json,),
            )
            return cur.fetchone()[0] > 0
    except sqlite3.Error as exc:
        logger.debug("log_event failure: %s", exc)
        return False
