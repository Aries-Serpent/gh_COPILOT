#!/usr/bin/env python3
"""Run a disaster recovery restore drill and log results.

The drill samples entries from ``rollback_logs`` within ``analytics.db``,
verifies their referenced backups exist, and logs restore outcomes. A
summary is published to the dashboard via ``_update_dashboard`` and an
evidence file is written under ``reports/disaster_recovery``.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

from enterprise_modules.compliance import validate_enterprise_operation
from utils.logging_utils import log_enterprise_operation, setup_enterprise_logging
from unified_monitoring_optimization_system import _update_dashboard

logger = setup_enterprise_logging()

WORKSPACE = Path(os.getenv("GH_COPILOT_WORKSPACE", ROOT))
REPORT_DIR = WORKSPACE / "reports" / "disaster_recovery"


def _sample_rollback_logs(db_path: Path, limit: int) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT target, backup, timestamp FROM rollback_logs ORDER BY RANDOM() LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def _restore_samples(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for entry in entries:
        backup_path = Path(entry["backup"])
        restored = backup_path.exists()
        status = "SUCCESS" if restored else "ERROR"
        log_enterprise_operation(
            "restore_drill",
            status,
            f"{entry['target']} <- {backup_path}",
        )
        results.append({**entry, "restored": restored})
    return results


def _schedule_next(now: datetime) -> datetime:
    return now + timedelta(days=30)


def run_restore_drill(db_path: Path, sample_size: int = 5) -> Path:
    """Execute a restore drill and return the evidence file path."""

    validate_enterprise_operation()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    samples = _sample_rollback_logs(db_path, sample_size)
    results = _restore_samples(samples)

    now = datetime.utcnow()
    report: Dict[str, Any] = {
        "run_at": now.isoformat(),
        "next_drill": _schedule_next(now).isoformat(),
        "sampled": results,
    }

    report_path = REPORT_DIR / f"{now.strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2))

    _update_dashboard(
        {
            "drill_sampled": len(results),
            "drill_success": sum(1 for r in results if r["restored"]),
        }
    )

    return report_path


if __name__ == "__main__":
    default_db = WORKSPACE / "databases" / "analytics.db"
    run_restore_drill(default_db)
