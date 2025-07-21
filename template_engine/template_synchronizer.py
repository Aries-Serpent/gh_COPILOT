from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
}

logger = logging.getLogger(__name__)


def _log_sync(log_conn: sqlite3.Connection, source: Path, result: str) -> None:
    log_conn.execute(
        "CREATE TABLE IF NOT EXISTS template_sync_log (timestamp TEXT, source TEXT, result TEXT)"
    )
    log_conn.execute(
        "INSERT INTO template_sync_log VALUES (?,?,?)",
        (datetime.now().isoformat(), str(source), result),
    )
    log_conn.commit()


def _gather_templates(db_paths: Iterable[Path]) -> dict[str, str]:
    templates: dict[str, str] = {}
    for path in db_paths:
        if not Path(path).exists():
            continue
        with sqlite3.connect(path) as conn:
            cur = conn.execute("SELECT name, template_content FROM templates")
            for name, content in cur.fetchall():
                if content:
                    templates[name] = content
    return templates


def synchronize_templates(db_paths: Iterable[Path], analytics_db: Path | None = None) -> None:
    analytics_db = analytics_db or Path("analytics.db")
    templates = _gather_templates(db_paths)
    with sqlite3.connect(analytics_db) as log_conn:
        for db in tqdm(list(db_paths), desc=f"{TEXT_INDICATORS['info']} sync", unit="db"):
            path = Path(db)
            result = "success"
            try:
                with sqlite3.connect(path) as conn:
                    cur = conn.cursor()
                    cur.execute("BEGIN")
                    for name, content in templates.items():
                        cur.execute(
                            "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                    invalid = cur.execute(
                        "SELECT COUNT(*) FROM templates WHERE template_content=''"
                    ).fetchone()[0]
                    if invalid:
                        raise ValueError("Empty templates detected")
                    conn.commit()
            except Exception as exc:  # noqa: BLE001
                logger.error(f"{TEXT_INDICATORS['error']} sync failed for {path}: {exc}")
                with sqlite3.connect(path) as conn:
                    conn.execute("ROLLBACK")
                result = "failure"
                _log_sync(log_conn, path, result)
                raise RuntimeError(f"Synchronization aborted for {path}")
            else:
                _log_sync(log_conn, path, result)
    logger.info(f"{TEXT_INDICATORS['success']} Template synchronization complete")
