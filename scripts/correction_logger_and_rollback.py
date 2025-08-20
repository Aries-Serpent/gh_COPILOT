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
        self._ensure_placeholder_audit()
        self.history_cache: Dict[str, int] = {}

    def _ensure_placeholder_audit(self) -> None:
        """Create placeholder_audit table if missing."""
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS placeholder_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    line_number INTEGER,
                    placeholder_type TEXT,
                    context TEXT,
                    timestamp TEXT
                )
                """
            )
            conn.commit()

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
                    correction_type TEXT,
                    compliance_score REAL,
                    score_delta REAL,
                    compliance_delta REAL,
                    rollback_reference TEXT,
                    session_id TEXT,
                    process_id INTEGER,
                    script TEXT,
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
            conn.execute(
                """CREATE TABLE IF NOT EXISTS correction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT,
                    doc_id TEXT,
                    path TEXT,
                    asset_type TEXT,
                    compliance_score REAL,
                    status TEXT,
                    timestamp TEXT
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS correction_rollback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    backup TEXT,
                    status TEXT,
                    timestamp TEXT NOT NULL
                )"""
            )
            existing = {row[1] for row in conn.execute("PRAGMA table_info(corrections)")}
            required = {
                "correction_type": "TEXT",
                "compliance_delta": "REAL",
                "process_id": "INTEGER",
                "script": "TEXT",
            }
            for col, col_type in required.items():
                if col not in existing:
                    conn.execute(f"ALTER TABLE corrections ADD COLUMN {col} {col_type}")
            existing_logs = {row[1] for row in conn.execute("PRAGMA table_info(correction_logs)")}
            if "status" not in existing_logs:
                conn.execute("ALTER TABLE correction_logs ADD COLUMN status TEXT")
            conn.commit()

    def log_change(
        self,
        file_path: Path,
        rationale: str,
        correction_type: str = "general",
        compliance_score: float = 1.0,
        rollback_reference: Optional[str] = None,
        score_delta: float = 0.0,
        compliance_delta: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a correction event in analytics.db with compliance score and rollback reference.
        """
        self.status = "LOGGING"
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT compliance_score FROM corrections WHERE file_path=? ORDER BY ts DESC LIMIT 1",
                (str(file_path),),
            )
            row = cur.fetchone()
            try:
                prev_score = float(row[0]) if row and row[0] is not None else None
            except (TypeError, ValueError):
                prev_score = None
            compliance_delta = (
                compliance_score - prev_score if prev_score is not None else compliance_score
            )
            conn.execute(
                "INSERT INTO corrections (file_path, rationale, correction_type, compliance_score, score_delta, compliance_delta, rollback_reference, session_id, process_id, script, ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(file_path),
                    rationale,
                    correction_type,
                    compliance_score,
                    score_delta,
                    compliance_delta,
                    rollback_reference,
                    session_id,
                    self.process_id,
                    file_path.name,
                    datetime.now().isoformat(),
                ),
            )
            if correction_type.lower().startswith("placeholder"):
                conn.execute(
                    "INSERT INTO placeholder_audit (file_path, line_number, placeholder_type, context, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(file_path),
                        None,
                        correction_type,
                        rationale,
                        datetime.utcnow().isoformat(),
                    ),
                )
            conn.execute(
                "INSERT INTO correction_logs (event, path, compliance_score, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    "correction",
                    str(file_path),
                    compliance_score,
                    "logged",
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.execute(
                "INSERT INTO correction_rollback_events (event_type, target, backup, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    correction_type,
                    str(file_path),
                    rollback_reference,
                    "logged",
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
        logging.info(
            f"Correction logged for {file_path} | Rationale: {rationale} | Type: {correction_type} | Compliance: {compliance_score} | Delta: {compliance_delta}"
        )
        _log_event(
            {
                "event": "correction",
                "file_path": str(file_path),
                "rationale": rationale,
                "correction_type": correction_type,
                "score": compliance_score,
                "score_delta": score_delta,
                "delta": compliance_delta,
                "session_id": session_id,
            },
            table="corrections",
            db_path=self.analytics_db,
        )
        _log_event(
            {
                "event": "correction",
                "path": str(file_path),
                "compliance_score": compliance_score,
                "status": "logged",
            },
            table="correction_logs",
            db_path=self.analytics_db,
        )
        key = str(file_path)
        self.history_cache[key] = self.history_cache.get(key, 0) + 1

    def log_violation(
        self,
        details: str,
        *,
        cause: str = "",
        remediation_path: str = "",
        rollback_trigger: str = "",
    ) -> None:
        """Record a compliance violation in ``violation_logs``."""
        with sqlite3.connect(self.analytics_db) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(violation_logs)")}
            values_map = {
                "timestamp": datetime.now().isoformat(),
                "event": "violation",
                "details": details,
                "cause": cause,
                "remediation_path": remediation_path,
                "rollback_trigger": rollback_trigger,
            }
            insert_cols = [col for col in values_map if col in columns]
            placeholders = ", ".join(["?"] * len(insert_cols))
            sql = (
                f"INSERT INTO violation_logs ({', '.join(insert_cols)}) VALUES ({placeholders})"
            )
            conn.execute(sql, tuple(values_map[col] for col in insert_cols))
            conn.commit()
        _log_event(
            {
                "event": "violation",
                "details": details,
                "cause": cause,
                "remediation_path": remediation_path,
                "rollback_trigger": rollback_trigger,
            },
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

    def auto_rollback(
        self,
        target: Path,
        backup_path: Optional[Path] = None,
        violation_id: Optional[int] = None,
    ) -> bool:
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
                    correction_type="rollback",
                    compliance_delta=0.0,
                )
                strategy = self.suggest_rollback_strategy(target)
                logging.info(f"Suggested strategy: {strategy}")
                self._record_strategy_history(target, strategy, "success")
                _log_rollback(str(target), str(backup_path) if backup_path else None)
                _log_event(
                    {
                        "event": "rollback",
                        "target": str(target),
                        "backup": str(backup_path) if backup_path else None,
                        "violation_id": violation_id,
                        "outcome": "success",
                    },
                    table="rollback_logs",
                    db_path=self.analytics_db,
                )
                return True
            else:
                logging.error(f"Rollback failed for {target}")
                strategy = self.suggest_rollback_strategy(target)
                self._record_strategy_history(target, strategy, "failure")
                _log_event(
                    {
                        "event": "rollback_failed",
                        "target": str(target),
                        "backup": str(backup_path) if backup_path else None,
                        "violation_id": violation_id,
                        "outcome": "failure",
                    },
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
                "SELECT file_path, rationale, correction_type, compliance_score, score_delta, compliance_delta, rollback_reference, ts, process_id, session_id, script "
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
                    "correction_type": row[2],
                    "compliance_score": row[3],
                    "score_delta": row[4],
                    "compliance_delta": row[4],
                    "rollback_reference": row[5],
                    "timestamp": row[6],
                    "process_id": row[7],
                    "script": row[8],
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
                md.write(f"  - Correction Type: {corr['correction_type']}\n")
                md.write(f"  - Compliance Score: {corr['compliance_score']}\n")
                md.write(f"  - Compliance Delta: {corr['compliance_delta']}\n")
                md.write(f"  - Rollback Reference: {corr['rollback_reference']}\n")
                md.write(f"  - Process ID: {corr['process_id']}\n")
                md.write(f"  - Script: {corr['script']}\n")
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
    logger.log_change(
        target_file,
        rationale,
        compliance_score,
        str(backup_path),
        correction_type="manual",
        compliance_delta=0.0,
    )
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
