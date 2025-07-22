"""Sync placeholder audit counts to dashboard."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def main(analytics_db: str | None = None, dashboard_dir: str | None = None) -> None:
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics = Path(analytics_db or workspace / "databases" / "analytics.db")
    dashboard = Path(dashboard_dir or workspace / "dashboard" / "compliance")
    dashboard.mkdir(parents=True, exist_ok=True)
    count = 0
    if analytics.exists():
        with sqlite3.connect(analytics) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "todo_fixme_tracking" in tables:
                count = conn.execute(
                    "SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='open'"
                ).fetchone()[0]
    data = {
        "timestamp": datetime.now().isoformat(),
        "open_placeholders": int(count),
    }
    (dashboard / "placeholder_sync.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
