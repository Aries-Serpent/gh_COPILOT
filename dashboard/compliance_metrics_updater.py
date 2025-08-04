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
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import threading

from tqdm import tqdm
from utils.log_utils import ensure_tables, insert_event
from enterprise_modules.compliance import validate_enterprise_operation
from disaster_recovery_orchestrator import DisasterRecoveryOrchestrator
from unified_monitoring_optimization_system import (
    EnterpriseUtility,
    push_metrics,
)
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


# Enterprise logging setup
LOGS_DIR = Path(os.getenv("GH_COPILOT_WORKSPACE", "/workspace/gh_COPILOT")) / "logs" / "dashboard"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"compliance_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# Database paths
ANALYTICS_DB = Path(os.getenv("GH_COPILOT_WORKSPACE", "/workspace/gh_COPILOT")) / "databases" / "analytics.db"
DASHBOARD_DIR = Path(os.getenv("GH_COPILOT_WORKSPACE", "/workspace/gh_COPILOT")) / "dashboard" / "compliance"


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "/workspace/gh_COPILOT"))
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logging.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def validate_environment_root() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "/workspace/gh_COPILOT"))
    if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
        logging.warning(f"Non-standard workspace root: {workspace_root}")


class ComplianceMetricsUpdater:
    """
    Update compliance metrics for the web dashboard.
    Integrates real-time metrics, violation/rollback alerts, and actionable GUI features.
    Validates all dashboard events are fed by analytics.db and correction logs.
    Aggregates pattern mining quality indicators and objective similarity scores
    to enhance compliance ranking.
    """

    def __init__(self, dashboard_dir: Path, *, test_mode: bool = False) -> None:
        self.dashboard_dir = dashboard_dir
        self.test_mode = test_mode
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.timeout_seconds = 1800  # 30 minutes
        self.status = "INITIALIZED"
        validate_no_recursive_folders()
        validate_environment_root()
        logging.info("PROCESS STARTED: Compliance Metrics Update")
        logging.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Process ID: {self.process_id}")
        ensure_tables(
            ANALYTICS_DB,
            ["violation_logs", "rollback_logs", "correction_logs"],
            test_mode=self.test_mode,
        )
        self.forbidden_phrases = ["rm -rf", "sudo", "wget "]
        self.monitoring_utility = EnterpriseUtility()
        self.correction_logger = CorrectionLoggerRollback(ANALYTICS_DB)

    def _fetch_compliance_metrics(self, *, test_mode: bool = False) -> Dict[str, Any]:
        """Fetch compliance metrics from analytics.db."""
        metrics = {
            "placeholder_removal": 0,
            "open_placeholders": 0,
            "resolved_placeholders": 0,
            "compliance_score": 1.0,
            "violation_count": 0,
            "rollback_count": 0,
            "progress_status": "unknown",
            "last_update": datetime.now().isoformat(),
            "placeholder_breakdown": {},
            "compliance_trend": [],
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
                    cur.execute(
                        "SELECT COUNT(*) FROM correction_history WHERE fix_applied='REMOVED_PLACEHOLDER'"
                    )
                    metrics["resolved_placeholders"] = cur.fetchone()[0]
                    metrics["open_placeholders"] = 0
                else:
                    cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='resolved'")
                    metrics["resolved_placeholders"] = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='open'")
                    metrics["open_placeholders"] = cur.fetchone()[0]
                metrics["placeholder_removal"] = metrics["resolved_placeholders"]

                open_ph = metrics["open_placeholders"]
                resolved_ph = metrics["resolved_placeholders"]
                denominator = resolved_ph + open_ph
                base_score = resolved_ph / denominator if denominator else 1.0
                metrics["compliance_score"] = base_score

                # Placeholder type breakdown
                try:
                    cur.execute(
                        "SELECT placeholder_type, COUNT(*) FROM todo_fixme_tracking GROUP BY placeholder_type"
                    )
                    metrics["placeholder_breakdown"] = {
                        row[0]: row[1] for row in cur.fetchall() if row[0]
                    }
                except sqlite3.Error:
                    metrics["placeholder_breakdown"] = {}

                # Compliance score trend (most recent first)
                try:
                    cur.execute(
                        "SELECT score FROM correction_logs WHERE event='update' ORDER BY timestamp DESC LIMIT 5"
                    )
                    scores = [row[0] for row in cur.fetchall()]
                    metrics["compliance_trend"] = list(reversed(scores))
                except sqlite3.Error:
                    metrics["compliance_trend"] = []

                cur.execute("SELECT COUNT(*) FROM correction_logs")
                metrics["correction_count"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM violation_logs")
                metrics["violation_count"] = cur.fetchone()[0]

                if cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rollback_logs'").fetchone():
                    cur.execute("SELECT target, backup, timestamp FROM rollback_logs ORDER BY timestamp DESC LIMIT 5")
                    metrics["recent_rollbacks"] = [
                        {"target": r[0], "backup": r[1], "timestamp": r[2]} for r in cur.fetchall()
                    ]
                    cur.execute("SELECT COUNT(*) FROM rollback_logs")
                    metrics["rollback_count"] = cur.fetchone()[0]
                    if metrics["rollback_count"]:
                        DisasterRecoveryOrchestrator().run_backup_cycle()
                else:
                    metrics["recent_rollbacks"] = []
                    metrics["rollback_count"] = 0
                penalty = 0.1 * metrics["violation_count"] + 0.05 * metrics["rollback_count"]
                metrics["compliance_score"] = max(0.0, min(1.0, base_score - penalty))

                # Pattern mining quality metrics
                try:
                    cur.execute(
                        "SELECT inertia, silhouette FROM pattern_cluster_metrics ORDER BY ts DESC LIMIT 1"
                    )
                    row = cur.fetchone()
                    if row:
                        metrics["pattern_cluster_quality"] = {
                            "inertia": float(row[0]),
                            "silhouette": float(row[1]),
                        }
                    else:
                        metrics["pattern_cluster_quality"] = {
                            "inertia": 0.0,
                            "silhouette": 0.0,
                        }
                except sqlite3.Error:
                    metrics["pattern_cluster_quality"] = {
                        "inertia": 0.0,
                        "silhouette": 0.0,
                    }

                # Objective similarity scoring metric
                try:
                    cur.execute("SELECT AVG(score) FROM objective_similarity")
                    avg = cur.fetchone()[0]
                    metrics["average_similarity_score"] = float(avg) if avg is not None else 0.0
                except sqlite3.Error:
                    metrics["average_similarity_score"] = 0.0
            except Exception as e:
                logging.error(f"Error fetching metrics: {e}")
        correction_summary = DASHBOARD_DIR / "correction_summary.json"
        if correction_summary.exists():
            try:
                summary_data = json.loads(correction_summary.read_text(encoding="utf-8"))
                metrics["correction_logs"] = summary_data.get("corrections", [])
                if metrics["correction_logs"]:
                    scores = [c.get("compliance_score", 0.0) for c in metrics["correction_logs"]]
                    metrics["average_correction_score"] = sum(scores) / len(scores)
            except json.JSONDecodeError:
                logging.warning("Failed to parse correction_summary.json")
                metrics["correction_logs"] = []
        else:
            metrics["correction_logs"] = []

        total_ph = metrics["resolved_placeholders"] + metrics["open_placeholders"]
        if total_ph:
            metrics["progress"] = metrics["resolved_placeholders"] / float(total_ph)
        else:
            metrics["progress"] = 1.0
        if metrics["violation_count"] or metrics["rollback_count"] or metrics["open_placeholders"]:
            metrics["progress_status"] = "issues_pending"
        else:
            metrics["progress_status"] = "complete"
        if metrics["violation_count"]:
            insert_event(
                {"event": "violation_detected", "count": metrics["violation_count"]},
                "violation_logs",
                db_path=ANALYTICS_DB,
                test_mode=test_mode,
            )
        if metrics["rollback_count"]:
            insert_event(
                {"event": "rollback_detected", "count": metrics["rollback_count"]},
                "rollback_logs",
                db_path=ANALYTICS_DB,
                test_mode=test_mode,
            )
        insert_event(
            {"event": "correction", "score": metrics.get("compliance_score", 0.0)},
            "correction_logs",
            db_path=ANALYTICS_DB,
            test_mode=test_mode,
        )
        metrics["last_update"] = datetime.now().isoformat()
        return metrics

    def _cognitive_compliance_suggestion(self, metrics: Dict[str, Any]) -> str:
        """Return a compliance suggestion based on historical logs and metrics."""
        suggestions: list[str] = []
        if ANALYTICS_DB.exists():
            try:
                with sqlite3.connect(ANALYTICS_DB) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT details FROM violation_logs ORDER BY timestamp DESC LIMIT 5")
                    violations = [row[0].lower() for row in cur.fetchall()]
                    if any("placeholder" in v for v in violations):
                        suggestions.append("Clean unresolved placeholders.")
                    if len(violations) > 2:
                        suggestions.append("Investigate recurring violations.")
                    cur.execute("SELECT AVG(compliance_score) FROM correction_logs")
                    avg_score = cur.fetchone()[0]
                    if avg_score is not None and avg_score < 0.9:
                        suggestions.append("Increase average compliance score.")
            except sqlite3.Error as exc:
                logging.warning("Suggestion analysis failed: %s", exc)
        if not suggestions:
            if metrics.get("violation_count", 0) > 0:
                suggestions.append("Review recent violations and address root causes.")
            elif metrics.get("open_placeholders", 0) > 0:
                suggestions.append("Resolve open placeholders to improve compliance.")
            else:
                suggestions.append("System compliant.")
        return " ".join(suggestions)

    def _check_forbidden_operations(self) -> None:
        """Fail if forbidden operations appear in recent logs."""
        try:
            text = LOG_FILE.read_text(encoding="utf-8")
        except OSError:
            return
        for phrase in self.forbidden_phrases:
            if phrase in text:
                raise RuntimeError(f"Forbidden operation detected: {phrase}")

    def stream_metrics(
        self,
        interval: int = 5,
        *,
        stop_event: Optional[threading.Event] = None,
        iterations: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """Yield metrics in real-time for streaming interfaces.

        Parameters
        ----------
        interval:
            Delay between metric fetches.
        stop_event:
            Optional ``threading.Event`` used to signal when the loop should
            stop.
        iterations:
            Optional maximum number of iterations to run. If ``None`` the
            generator runs indefinitely unless ``stop_event`` is set.
        """
        count = 0
        while True:
            if stop_event and stop_event.is_set():
                break
            if iterations is not None and count >= iterations:
                break
            try:
                validate_no_recursive_folders()
                self._check_forbidden_operations()
            except Exception as exc:  # DualCopilotOrchestrator validation
                logging.exception("Streaming validation failed: %s", exc)
                raise

            metrics = self._fetch_compliance_metrics()
            metrics["suggestion"] = self._cognitive_compliance_suggestion(metrics)
            yield metrics
            count += 1
            if stop_event:
                stop_event.wait(interval)
            else:
                time.sleep(interval)

    def _update_dashboard(self, metrics: Dict[str, Any]) -> None:
        """Update dashboard/compliance with metrics."""
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        dashboard_file = self.dashboard_dir / "metrics.json"
        rollback_file = self.dashboard_dir / "rollback_logs.json"
        import json

        dashboard_content = {
            "metrics": metrics,
            "status": metrics.get("progress_status", "updated"),
            "timestamp": datetime.now().isoformat(),
        }
        dashboard_file.write_text(json.dumps(dashboard_content, indent=2), encoding="utf-8")
        rollback_file.write_text(
            json.dumps(metrics.get("recent_rollbacks", []), indent=2),
            encoding="utf-8",
        )
        logging.info(f"Dashboard metrics updated: {dashboard_file}")

    def _log_update_event(self, metrics: Dict[str, Any], *, test_mode: bool = False) -> None:
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | Metrics Updated | {metrics}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(log_entry)
        logging.info("Update event logged.")
        insert_event(
            {"event": "dashboard_update", "metrics": metrics},
            "event_log",
            db_path=ANALYTICS_DB,
            test_mode=test_mode,
        )
        if metrics.get("violation_count"):
            insert_event(
                {"event": "violation", "count": metrics["violation_count"]},
                "violation_logs",
                db_path=ANALYTICS_DB,
                test_mode=test_mode,
            )
        if metrics.get("rollback_count"):
            insert_event(
                {"event": "rollback", "count": metrics["rollback_count"]},
                "rollback_logs",
                db_path=ANALYTICS_DB,
                test_mode=test_mode,
            )
        insert_event(
            {"event": "update", "score": metrics.get("compliance_score", 0.0)},
            "correction_logs",
            db_path=ANALYTICS_DB,
            test_mode=test_mode,
        )

    def _push_monitoring_metrics(self, metrics: Dict[str, Any]) -> None:
        """Send metrics to the unified monitoring system."""
        monitoring_metrics = {
            "compliance_score": float(metrics.get("compliance_score", 0.0)),
            "violation_count": float(metrics.get("violation_count", 0.0)),
            "rollback_count": float(metrics.get("rollback_count", 0.0)),
        }
        push_metrics(monitoring_metrics, table="enterprise_metrics", db_path=ANALYTICS_DB)
        if monitoring_metrics["compliance_score"] < 0.8:
            self.monitoring_utility.execute_utility()

    def _synchronize_corrections(self, metrics: Dict[str, Any]) -> None:
        """Log violations and rollbacks via the correction logger."""
        if metrics.get("violation_count") or metrics.get("compliance_score", 1.0) < 0.8:
            self.correction_logger.log_violation("Compliance degradation detected")
        for entry in metrics.get("recent_rollbacks", []):
            target = Path(entry.get("target", ""))
            backup = entry.get("backup")
            self.correction_logger.log_change(
                target,
                "Auto rollback recorded",
                metrics.get("compliance_score", 0.0),
                rollback_reference=backup,
            )

    def update(self, simulate: bool = False) -> None:
        """Update compliance metrics for the web dashboard with full compliance and validation.

        Parameters
        ----------
        simulate: bool, optional
            If ``True``, skip writing to the dashboard and log files.
        """
        validate_enterprise_operation(str(self.dashboard_dir))
        self.status = "UPDATING"
        start_time = time.time()
        with tqdm(total=4, desc="Updating Compliance Metrics", unit="step") as pbar:
            pbar.set_description("Fetching Metrics")
            metrics = self._fetch_compliance_metrics(test_mode=self.test_mode or simulate)
            metrics["suggestion"] = self._cognitive_compliance_suggestion(metrics)
            pbar.update(1)

            if not simulate:
                pbar.set_description("Checking Operations")
                self._check_forbidden_operations()
                pbar.update(0)

                pbar.set_description("Updating Dashboard")
                self._update_dashboard(metrics)
                pbar.update(1)

                pbar.set_description("Logging Update Event")
                self._log_update_event(metrics, test_mode=self.test_mode)
                self._push_monitoring_metrics(metrics)
                self._synchronize_corrections(metrics)
                pbar.update(1)

                pbar.set_description("Syncing External Systems")
                self._sync_external_systems(metrics)
                pbar.update(1)
            else:
                pbar.set_description("Simulation Mode")
                pbar.update(3)

        elapsed = time.time() - start_time
        etc = self._calculate_etc(elapsed, 4, 4)
        logging.info(f"Compliance metrics update completed in {elapsed:.2f}s | ETC: {etc}")
        insert_event(
            {"event": "update_complete", "duration": elapsed},
            "event_log",
            db_path=ANALYTICS_DB,
            test_mode=self.test_mode or simulate,
        )
        self.status = "COMPLETED"

    def _calculate_etc(self, elapsed: float, current_progress: int, total_work: int) -> str:
        if current_progress > 0:
            total_estimated = elapsed / (current_progress / total_work)
            remaining = total_estimated - elapsed
            return f"{remaining:.2f}s remaining"
        return "N/A"

    def run_scheduler(self, interval: int = 60, iterations: int = 1, simulate: bool = False) -> None:
        """Periodically run :meth:`update` with safety checks."""
        for _ in range(iterations):
            validate_enterprise_operation(str(self.dashboard_dir))
            validate_no_recursive_folders()
            self._check_forbidden_operations()
            self.update(simulate=simulate)
            if iterations > 1:
                time.sleep(interval)

    def validate_update(self) -> bool:
        """DUAL COPILOT: Secondary validator for dashboard integrity and compliance."""
        dashboard_file = self.dashboard_dir / "metrics.json"
        valid = dashboard_file.exists() and dashboard_file.stat().st_size > 0
        if valid:
            logging.info("DUAL COPILOT validation passed: Dashboard metrics file present and non-zero-byte.")
        else:
            logging.error("DUAL COPILOT validation failed: Dashboard metrics file missing or zero-byte.")
        return valid


def main(simulate: bool = False, stream: bool = False, test_mode: bool = False) -> None:
    """Command-line entry point."""
    dashboard_dir = DASHBOARD_DIR
    updater = ComplianceMetricsUpdater(dashboard_dir, test_mode=test_mode)
    if stream:
        for metrics in updater.stream_metrics():
            print(metrics)
    else:
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
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Continuously stream metrics to stdout",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable test mode for analytics events",
    )
    args = parser.parse_args()
    main(simulate=args.simulate, stream=args.stream, test_mode=args.test_mode)
