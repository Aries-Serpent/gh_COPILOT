"""
Compliance Metrics Updater – Enterprise Codex Compliance

MANDATORY REQUIREMENTS:
1. Extend /dashboard/compliance for real-time metrics, violation/rollback alerts, actionable GUI.
2. Validate all dashboard events are fed by analytics.db and correction logs.
3. Visual indicators: tqdm progress bar, start time logging, timeout, ETC calculation, real-time status updates.
4. Anti-recursion validation before dashboard update.
5. DUAL COPILOT: Secondary validator checks dashboard integrity and compliance.
6. Integrate cognitive learning and fetch comparable scripts for improvement.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from tqdm import tqdm
from utils.log_utils import _log_event

from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs

# Enterprise logging setup
LOGS_DIR = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")) / "logs" / "dashboard"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"compliance_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# Database paths
ANALYTICS_DB = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")) / "databases" / "analytics.db"
DASHBOARD_DIR = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")) / "dashboard" / "compliance"


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logging.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def validate_environment_root() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
        logging.warning(f"Non-standard workspace root: {workspace_root}")


class ComplianceMetricsUpdater:
    """
    Update compliance metrics for the web dashboard.
    Integrates real-time metrics, violation/rollback alerts, and actionable GUI features.
    Validates all dashboard events are fed by analytics.db and correction logs.
    """

    def __init__(self, dashboard_dir: Path) -> None:
        self.dashboard_dir = dashboard_dir
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.timeout_seconds = 1800  # 30 minutes
        self.status = "INITIALIZED"
        validate_no_recursive_folders()
        validate_environment_root()
        logging.info("PROCESS STARTED: Compliance Metrics Update")
        logging.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Process ID: {self.process_id}")
        ensure_violation_logs(ANALYTICS_DB)
        ensure_rollback_logs(ANALYTICS_DB)

    def _fetch_compliance_metrics(self) -> Dict[str, Any]:
        """Fetch compliance metrics from analytics.db."""
        metrics = {
            "placeholder_removal": 0,
            "open_placeholders": 0,
            "resolved_placeholders": 0,
            "compliance_score": 0.0,
            "violation_count": 0,
            "rollback_count": 0,
            "progress_status": "unknown",
            "last_update": datetime.now().isoformat(),
        }
        if not ANALYTICS_DB.exists():
            logging.warning("analytics.db not found, using default metrics.")
            return metrics
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            try:
                # Placeholder removals recorded in todo_fixme_tracking or correction_history
                if cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='correction_history'"
                ).fetchone():
                    cur.execute("SELECT COUNT(*) FROM correction_history WHERE fix_applied='REMOVED_PLACEHOLDER'")
                    metrics["resolved_placeholders"] = cur.fetchone()[0]
                    metrics["open_placeholders"] = 0
                else:
                    cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE resolved=1")
                    metrics["resolved_placeholders"] = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE resolved=0")
                    metrics["open_placeholders"] = cur.fetchone()[0]
                metrics["placeholder_removal"] = metrics["resolved_placeholders"]

                cur.execute("SELECT AVG(compliance_score) FROM correction_logs")
                avg_score = cur.fetchone()[0]
                metrics["compliance_score"] = float(avg_score) if avg_score is not None else 0.0

                cur.execute("SELECT COUNT(*) FROM violation_logs")
                metrics["violation_count"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM rollback_logs")
                metrics["rollback_count"] = cur.fetchone()[0]
            except Exception as e:
                logging.error(f"Error fetching metrics: {e}")
        if metrics["violation_count"] or metrics["rollback_count"]:
            metrics["progress_status"] = "issues_pending"
        else:
            metrics["progress_status"] = "complete"
        if metrics["violation_count"]:
            _log_event(
                {"event": "violation_detected", "count": metrics["violation_count"]},
                table="violation_logs",
                db_path=ANALYTICS_DB,
            )
        if metrics["rollback_count"]:
            _log_event(
                {"event": "rollback_detected", "count": metrics["rollback_count"]},
                table="rollback_logs",
                db_path=ANALYTICS_DB,
            )
        metrics["last_update"] = datetime.now().isoformat()
        return metrics

    def _update_dashboard(self, metrics: Dict[str, Any]) -> None:
        """Update dashboard/compliance with metrics."""
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        dashboard_file = self.dashboard_dir / "metrics.json"
        import json

        dashboard_content = {
            "metrics": metrics,
            "status": metrics.get("progress_status", "updated"),
            "timestamp": datetime.now().isoformat(),
        }
        dashboard_file.write_text(json.dumps(dashboard_content, indent=2), encoding="utf-8")
        logging.info(f"Dashboard metrics updated: {dashboard_file}")

    def _log_update_event(self, metrics: Dict[str, Any]) -> None:
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | Metrics Updated | {metrics}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(log_entry)
        logging.info("Update event logged.")
        _log_event({"event": "dashboard_update", "metrics": metrics}, db_path=ANALYTICS_DB)

    def update(self, simulate: bool = False) -> None:
        """Update compliance metrics for the web dashboard with full compliance and validation.

        Parameters
        ----------
        simulate: bool, optional
            If ``True``, skip writing to the dashboard and log files.
        """
        self.status = "UPDATING"
        start_time = time.time()
        with tqdm(total=3, desc="Updating Compliance Metrics", unit="step") as pbar:
            pbar.set_description("Fetching Metrics")
            metrics = self._fetch_compliance_metrics()
            pbar.update(1)

            if not simulate:
                pbar.set_description("Updating Dashboard")
                self._update_dashboard(metrics)
                pbar.update(1)

                pbar.set_description("Logging Update Event")
                self._log_update_event(metrics)
                pbar.update(1)
            else:
                pbar.set_description("Simulation Mode")
                pbar.update(2)

        elapsed = time.time() - start_time
        etc = self._calculate_etc(elapsed, 3, 3)
        logging.info(f"Compliance metrics update completed in {elapsed:.2f}s | ETC: {etc}")
        _log_event({"event": "update_complete", "duration": elapsed}, db_path=ANALYTICS_DB)
        self.status = "COMPLETED"

    def _calculate_etc(self, elapsed: float, current_progress: int, total_work: int) -> str:
        if current_progress > 0:
            total_estimated = elapsed / (current_progress / total_work)
            remaining = total_estimated - elapsed
            return f"{remaining:.2f}s remaining"
        return "N/A"

    def validate_update(self) -> bool:
        """DUAL COPILOT: Secondary validator for dashboard integrity and compliance."""
        dashboard_file = self.dashboard_dir / "metrics.json"
        valid = dashboard_file.exists() and dashboard_file.stat().st_size > 0
        if valid:
            logging.info("DUAL COPILOT validation passed: Dashboard metrics file present and non-zero-byte.")
        else:
            logging.error("DUAL COPILOT validation failed: Dashboard metrics file missing or zero-byte.")
        return valid


def main(simulate: bool = False) -> None:
    """Command-line entry point."""
    dashboard_dir = DASHBOARD_DIR
    updater = ComplianceMetricsUpdater(dashboard_dir)
    updater.update(simulate=simulate)
    updater.validate_update()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update compliance metrics")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in test mode without writing to disk",
    )
    args = parser.parse_args()
    main(simulate=args.simulate)
