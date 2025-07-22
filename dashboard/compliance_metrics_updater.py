#!/usr/bin/env python3
"""Update compliance metrics for the web dashboard."""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict

from tqdm import tqdm

DASHBOARD_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")


def fetch_metrics() -> Dict[str, Any]:
    if not ANALYTICS_DB.exists():
        return {"findings": 0}
    with sqlite3.connect(ANALYTICS_DB) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking")
        count = cur.fetchone()[0]
    return {"findings": count}


def update_dashboard() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    metrics = fetch_metrics()
    with tqdm(total=1, desc="dashboard", unit="step") as bar:
        data = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **metrics}
        (DASHBOARD_DIR / "metrics.json").write_text(json.dumps(data, indent=2))
        bar.update(1)
    logging.info("[INFO] dashboard metrics updated")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    update_dashboard()
