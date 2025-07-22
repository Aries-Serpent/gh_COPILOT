#!/usr/bin/env python3
"""Correction logging and rollback utility.

This script records modifications to the workspace in ``analytics.db`` and
provides a basic rollback mechanism. Each change is tracked with a timestamp and
reason to support enterprise compliance requirements.
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Optional

from tqdm import tqdm

DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
BACKUP_ROOT = Path(Path.home(), "gh_COPILOT_corrections")


class CorrectionLogger:
    def __init__(self, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> None:
        self.analytics_db = analytics_db
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                backup_path TEXT,
                reason TEXT,
                ts TEXT
            )"""
            )
            conn.commit()

    # ------------------------------------------------------------------
    def log_change(self, file_path: Path, reason: str) -> Path:
        backup_dir = BACKUP_ROOT
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"{file_path.name}.{int(time.time())}.bak"
        shutil.copy2(file_path, backup)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "INSERT INTO corrections (file_path, backup_path, reason, ts) VALUES (?, ?, ?, ?)",
                (str(file_path), str(backup), reason, time.strftime("%Y-%m-%dT%H:%M:%S")),
            )
            conn.commit()
        return backup

    # ------------------------------------------------------------------
    def rollback(self, entry_id: int) -> bool:
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT file_path, backup_path FROM corrections WHERE id=?", (entry_id,)
            )
            row = cur.fetchone()
            if not row:
                return False
            file_path, backup_path = map(Path, row)
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                return True
        return False


def main(file_path: Optional[str] = None, reason: str = "update") -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not file_path:
        logging.error("[ERROR] file_path required")
        return
    logger = CorrectionLogger()
    with tqdm(total=1, desc="logging") as bar:
        backup = logger.log_change(Path(file_path), reason)
        bar.update(1)
    logging.info("Logged change, backup stored at %s", backup)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="File to log")
    parser.add_argument("--reason", default="update", help="Reason for change")
    args = parser.parse_args()
    main(args.file_path, args.reason)
