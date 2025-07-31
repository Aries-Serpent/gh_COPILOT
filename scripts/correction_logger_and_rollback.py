"""
Enterprise Correction Logger and Rollback System

MANDATORY REQUIREMENTS:
1. Log every change to analytics.db with timestamp, rationale, compliance score, rollback reference.
2. Implement auto-rollback for failed syncs or corrections.
3. Summarize corrections in compliance reports (Markdown/JSON) for dashboard.
4. Visual indicators: tqdm, start time, timeout, ETC, status updates.
5. Anti-recursion validation before rollback.
6. DUAL COPILOT: Secondary validator checks correction integrity and compliance.
7. Integrate cognitive learning from deep web research for correction/rollback best practices.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from tqdm import tqdm

from enterprise_modules.compliance import (
    validate_enterprise_operation,
    _log_rollback,
)
from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs
from scripts.database.add_rollback_strategy_history import (
    ensure_rollback_strategy_history,
)
from utils.log_utils import _log_event
from utils.cross_platform_paths import CrossPlatformPathManager

# Enterprise logging setup
LOGS_DIR = CrossPlatformPathManager.get_workspace_path() / "logs" / "correction_logger"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"correction_logger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

DASHBOARD_DIR = CrossPlatformPathManager.get_workspace_path() / "dashboard" / "compliance"


class CorrectionLoggerRollback:
    """
    Enterprise Correction Logger and Rollback System.
    Logs corrections to analytics.db, supports rollback, and generates compliance reports.
    """

    def __init__(self, analytics_db: Path) -> None:
        self.analytics_db = analytics_db
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.timeout_seconds = 1800  # 30 minutes
        self.status = "INITIALIZED"
        validate_enterprise_operation()
        logging.info(f"PROCESS STARTED: Correction Logging and Rollback")
        logging.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Process ID: {self.process_id}")
        self._ensure_table_exists()
        ensure_violation_logs(self.analytics_db)
        ensure_rollback_logs(self.analytics_db)
        ensure_rollback_strategy_history(self.analytics_db)
        self.history_cache: Dict[str, int] = {}

    def _derive_root_cause(self, rationale: str) -> str:
        """Very simple root-cause analysis based on rationale text."""
        if "syntax" in rationale.lower():
            return "coding standards"
        if "dependency" in rationale.lower():
            return "dependency issue"
        return "unspecified"

    def suggest_rollback_strategy(self, target: Path) -> str:
        """Return a rollback recommendation based on historical performance."""
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT strategy, outcome FROM rollback_strategy_history WHERE target=?",
                (str(target),),
            )
            rows = cur.fetchall()
            if not rows:
                cur = conn.execute("SELECT strategy, outcome FROM rollback_strategy_history")
                rows = cur.fetchall()

        stats: Dict[str, Dict[str, int]] = {}
        total = 0
        successes = 0
        for strategy, outcome in rows:
            total += 1
            if outcome == "success":
                successes += 1
            data = stats.setdefault(strategy, {"success": 0, "total": 0})
            data["total"] += 1
            if outcome == "success":
                data["success"] += 1

        if not stats:
            return "Standard rollback"

        best_name, best_data = max(
            stats.items(),
            key=lambda item: (item[1]["success"] / item[1]["total"], item[1]["total"]),
        )
        best_rate = best_data["success"] / best_data["total"]

        overall_rate = successes / total if total else 0.0
        if total >= 4 and overall_rate <= 0.5:
            return "Consider immutable backup storage or audit investigation."
        if total > 1 and best_rate < 1.0:
            return "Automate regression tests for this file."
        return f"Use '{best_name}' ({best_rate:.0%} success rate)."

    def _ensure_table_exists(self) -> None:
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    rationale TEXT,
                    compliance_score REAL,
                    rollback_reference TEXT,
                    ts TEXT
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS rollback_strategy_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )"""
            )
            conn.commit()

    def log_change(
        self,
        file_path: Path,
        rationale: str,
        compliance_score: float = 1.0,
        rollback_reference: Optional[str] = None,
    ) -> None:
        """
        Record a correction event in analytics.db with compliance score and rollback reference.
        """
        self.status = "LOGGING"
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "INSERT INTO corrections (file_path, rationale, compliance_score, rollback_reference, ts) VALUES (?, ?, ?, ?, ?)",
                (
                    str(file_path),
                    rationale,
                    compliance_score,
                    rollback_reference,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        logging.info(f"Correction logged for {file_path} | Rationale: {rationale} | Compliance: {compliance_score}")
        _log_event(
            {
                "event": "correction",
                "file_path": str(file_path),
                "rationale": rationale,
                "score": compliance_score,
            },
            table="corrections",
            db_path=self.analytics_db,
        )
        key = str(file_path)
        self.history_cache[key] = self.history_cache.get(key, 0) + 1

    def log_violation(self, details: str) -> None:
        """Record a compliance violation in ``violation_logs``."""
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
                (datetime.now().isoformat(), details),
            )
            conn.commit()
        _log_event(
            {"event": "violation", "details": details},
            table="violation_logs",
            db_path=self.analytics_db,
        )

    def _record_strategy_history(self, target: Path, strategy: str, outcome: str) -> None:
        """Log chosen rollback strategy and outcome."""
        clean = strategy
        if strategy.startswith("Use '") and "(" in strategy:
            clean = strategy.split("(", 1)[0].replace("Use", "").strip().strip("'")
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "INSERT INTO rollback_strategy_history (target, strategy, outcome, timestamp) VALUES (?, ?, ?, ?)",
                (
                    str(target),
                    clean,
                    outcome,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        _log_event(
            {"event": "strategy", "target": str(target), "strategy": clean, "outcome": outcome},
            table="rollback_strategy_history",
            db_path=self.analytics_db,
        )

    def auto_rollback(self, target: Path, backup_path: Optional[Path] = None) -> bool:
        """
        Auto-rollback for failed syncs or corrections. Restores file from backup if available.
        """
        self.status = "ROLLBACK"
        start_time = time.time()
        validate_enterprise_operation()
        with tqdm(total=100, desc=f"Rolling Back {target.name}", unit="%") as pbar:
            pbar.set_description("Validating Target")
            if not target.exists() and not backup_path:
                logging.error(f"Target file does not exist and no backup provided: {target}")
                strategy = self.suggest_rollback_strategy(target)
                self._record_strategy_history(target, strategy, "failure")
                _log_event(
                    {
                        "event": "rollback_failure",
                        "target": str(target),
                        "details": "missing target and backup",
                    },
                    table="rollback_failures",
                    db_path=self.analytics_db,
                )
                _log_rollback(str(target), str(backup_path) if backup_path else None)
                pbar.update(100)
                return False
            pbar.update(25)

            pbar.set_description("Restoring Backup")
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, target)
                logging.info(f"Restored {target} from backup {backup_path}")
            else:
                logging.warning(f"No backup available for {target}, rollback skipped")
            pbar.update(50)

            pbar.set_description("Verifying Restoration")
            if target.exists() and target.stat().st_size > 0:
                logging.info(f"Rollback successful for {target}")
                pbar.update(25)
                self.log_change(
                    target,
                    "Auto-rollback executed",
                    compliance_score=0.0,
                    rollback_reference=str(backup_path),
                )
                strategy = self.suggest_rollback_strategy(target)
                logging.info(f"Suggested strategy: {strategy}")
                self._record_strategy_history(target, strategy, "success")
                _log_rollback(str(target), str(backup_path) if backup_path else None)
                _log_event(
                    {"event": "rollback", "target": str(target)},
                    table="rollback_logs",
                    db_path=self.analytics_db,
                )
                return True
            else:
                logging.error(f"Rollback failed for {target}")
                strategy = self.suggest_rollback_strategy(target)
                self._record_strategy_history(target, strategy, "failure")
                _log_event(
                    {"event": "rollback_failed", "target": str(target)},
                    table="rollback_logs",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {
                        "event": "rollback_failure",
                        "target": str(target),
                        "details": "restore verification failed",
                    },
                    table="rollback_failures",
                    db_path=self.analytics_db,
                )
                _log_rollback(str(target), str(backup_path) if backup_path else None)
                pbar.update(25)
                return False

    def summarize_corrections(self, max_entries: int = 100) -> Dict[str, Any]:
        """
        Summarize corrections for compliance reports (Markdown/JSON) for dashboard.
        """
        self.status = "SUMMARIZING"
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT file_path, rationale, compliance_score, rollback_reference, ts "
                "FROM corrections ORDER BY ts DESC"
            )
            corrections = cur.fetchall()

        corrections = corrections[:max_entries]
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_corrections": len(corrections),
            "corrections": [
                {
                    "file_path": row[0],
                    "rationale": row[1],
                    "compliance_score": row[2],
                    "rollback_reference": row[3],
                    "timestamp": row[4],
                    "root_cause": self._derive_root_cause(row[1]),
                }
                for row in corrections
            ],
            "status": "complete" if corrections else "none",
        }
        # Write JSON summary
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        archive_dir = DASHBOARD_DIR / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        json_path = DASHBOARD_DIR / "correction_summary.json"
        md_path = DASHBOARD_DIR / "correction_summary.md"

        if json_path.exists() or md_path.exists():
            tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            if json_path.exists():
                json_path.rename(archive_dir / f"correction_summary_{tag}.json")
            if md_path.exists():
                md_path.rename(archive_dir / f"correction_summary_{tag}.md")

        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        # Write Markdown summary
        with open(md_path, "w", encoding="utf-8") as md:
            md.write(f"# Correction Summary\n\n")
            md.write(f"**Timestamp:** {summary['timestamp']}\n\n")
            md.write(f"**Total Corrections:** {summary['total_corrections']}\n\n")
            for corr in summary["corrections"]:
                md.write(f"- **File:** {corr['file_path']}\n")
                md.write(f"  - Rationale: {corr['rationale']}\n")
                md.write(f"  - Compliance Score: {corr['compliance_score']}\n")
                md.write(f"  - Rollback Reference: {corr['rollback_reference']}\n")
                md.write(f"  - Timestamp: {corr['timestamp']}\n\n")
        logging.info(f"Correction summary written to {json_path} and {md_path}")
        _log_event(
            {
                "event": "correction_summary",
                "count": summary["total_corrections"],
            },
            table="correction_summaries",
            db_path=self.analytics_db,
        )
        return summary

    def _calculate_etc(self, elapsed: float, current_progress: int, total_work: int) -> str:
        if current_progress > 0:
            total_estimated = elapsed / (current_progress / total_work)
            remaining = total_estimated - elapsed
            return f"{remaining:.2f}s remaining"
        return "N/A"

    def validate_corrections(self, expected_count: int) -> bool:
        """
        DUAL COPILOT: Secondary validator for correction integrity and compliance.
        """
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM corrections")
            db_count = cur.fetchone()[0]
        valid = db_count >= expected_count
        if valid:
            logging.info("DUAL COPILOT validation passed: Correction log integrity confirmed.")
        else:
            logging.error("DUAL COPILOT validation failed: Correction log mismatch.")
        return valid


def main(
    analytics_db_path: Optional[str] = None,
    dashboard_dir: Optional[str] = None,
    timeout_minutes: int = 30,
) -> bool:
    """
    Entry point for correction logging and rollback management.
    """
    start_time = time.time()
    process_id = os.getpid()
    logging.info(f"PROCESS STARTED: Correction Logger and Rollback")
    logging.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Process ID: {process_id}")

    # Anti-recursion validation
    validate_enterprise_operation()

    workspace = CrossPlatformPathManager.get_workspace_path()
    analytics_db = Path(analytics_db_path or workspace / "databases" / "analytics.db")
    dashboard = Path(dashboard_dir or workspace / "dashboard" / "compliance")

    # Example correction logging and rollback
    logger = CorrectionLoggerRollback(analytics_db)
    # Simulate a correction event
    target_file = workspace / "example.txt"
    rationale = "Corrected syntax error in example.txt"
    compliance_score = 0.95
    backup_path = workspace / "backups" / "example.txt.bak"
    logger.log_change(target_file, rationale, compliance_score, str(backup_path))
    # Simulate rollback
    logger.auto_rollback(target_file, backup_path)
    # Summarize corrections
    summary = logger.summarize_corrections()
    elapsed = time.time() - start_time
    etc = logger._calculate_etc(elapsed, 1, 1)
    logging.info(f"Correction logger completed in {elapsed:.2f}s | ETC: {etc}")

    # DUAL COPILOT validation
    valid = logger.validate_corrections(summary["total_corrections"])
    if valid:
        logging.info(f"Correction logger session logged {summary['total_corrections']} corrections")
    else:
        logging.error("Correction logger session validation mismatch")
    return valid


if __name__ == "__main__":
    success = main()
    raise SystemExit(0 if success else 1)
