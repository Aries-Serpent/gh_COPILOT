#!/usr/bin/env python3
"""Cross-reference new files with dashboard and analytics records."""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import List

from tqdm import tqdm

PRODUCTION_DB = Path("databases/production.db")
ANALYTICS_DB = Path("databases/analytics.db")
DASHBOARD_DIR = Path("dashboard/compliance")


def fetch_reference_files() -> List[str]:
    if not PRODUCTION_DB.exists():
        return []
    with sqlite3.connect(PRODUCTION_DB) as conn:
        cur = conn.execute("SELECT file_path FROM reference_files")
        return [row[0] for row in cur.fetchall()]


def validate_files(files: List[Path]) -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    mismatches: List[str] = []
    with tqdm(total=len(files), desc="validate", unit="file") as bar:
        for f in files:
            if str(f) not in fetch_reference_files():
                mismatches.append(str(f))
            bar.update(1)
    (DASHBOARD_DIR / "cross_reference.json").write_text(json.dumps(mismatches, indent=2))
    logging.info("[INFO] cross-reference complete: %d mismatches", len(mismatches))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    validate_files([p for p in Path.cwd().rglob("*.py")])
