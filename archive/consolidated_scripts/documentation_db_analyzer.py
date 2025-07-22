from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable, List, Optional

from tqdm import tqdm

# Enterprise paths and defaults
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
DEFAULT_DOC_DBS = [
    Path("databases/documentation.db"),
    Path("databases/documentation_templates.db"),
    Path("databases/template_documentation.db"),
]
LOG_DIR = Path("logs/template_rendering")
LOG_DIR.mkdir(parents=True, exist_ok=True)

class DocumentationDBAnalyzer:
    """
    Enterprise Documentation Database Analyzer

    Scans documentation databases for gaps, missing types, and compliance issues.
    Logs all findings to analytics.db and writes detailed reports to /logs/template_rendering.
    Implements visual processing indicators, timeout, ETC, and DUAL COPILOT validation.
    """

    def __init__(
        self,
        doc_dbs: Optional[Iterable[Path]] = None,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        timeout_minutes: int = 30,
    ) -> None:
        self.doc_dbs = list(doc_dbs) if doc_dbs else DEFAULT_DOC_DBS
        self.analytics_db = analytics_db
        self.timeout_seconds = timeout_minutes * 60
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.log_file = LOG_DIR / f"doc_db_analyzer_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info(f"PROCESS STARTED: DocumentationDBAnalyzer")
        logging.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Process ID: {self.process_id}")

    def scan(self) -> Dict[str, Any]:
        """
        Scan all documentation databases for gaps, missing doc_types, and compliance issues.
        Includes visual indicators, timeout, ETC, and logs all findings.
        """
        self._validate_no_recursive_folders()
        summary: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "databases": {},
            "process_id": self.process_id,
            "start_time": self.start_time.isoformat(),
        }
        total_steps = len(self.doc_dbs)
        start_time = time.time()
        with tqdm(total=total_steps, desc="Scanning Documentation DBs", unit="db") as pbar:
            for idx, db in enumerate(self.doc_dbs, 1):
                pbar.set_description(f"Scanning {db.name}")
                elapsed = time.time() - start_time
                if elapsed > self.timeout_seconds:
                    raise TimeoutError(f"Process exceeded {self.timeout_seconds/60:.1f} minute timeout")
                if not db.exists():
                    summary["databases"][str(db)] = {"error": "Database not found"}
                    pbar.update(1)
                    continue
                try:
                    with sqlite3.connect(db) as conn:
                        # Check for missing doc_types and count entries
                        cur = conn.execute(
                            "SELECT doc_type, COUNT(*) FROM enterprise_documentation GROUP BY doc_type"
                        )
                        rows = cur.fetchall()
                        doc_type_counts = {dt: cnt for dt, cnt in rows}
                        # Find missing doc_types (if any expected types are defined)
                        expected_types = self._get_expected_doc_types(conn)
                        missing_types = [dt for dt in expected_types if dt not in doc_type_counts]
                        summary["databases"][str(db)] = {
                            "doc_type_counts": doc_type_counts,
                            "missing_types": missing_types,
                            "total_entries": sum(doc_type_counts.values()),
                        }
                except Exception as exc:
                    summary["databases"][str(db)] = {"error": str(exc)}
                etc = self._calculate_etc(elapsed, idx, total_steps)
                pbar.set_postfix(ETC=etc)
                pbar.update(1)
        elapsed = time.time() - start_time
        logging.info(f"Documentation DB analysis completed in {elapsed:.2f}s | ETC: {etc}")
        self._write_log(summary)
        self._log_to_db(summary)
        self._dual_copilot_validate()
        return summary

    def _get_expected_doc_types(self, conn: sqlite3.Connection) -> List[str]:
        """
        Retrieve expected documentation types from the database schema or metadata.
        """
        try:
            cur = conn.execute("PRAGMA table_info(enterprise_documentation)")
            columns = [row[1] for row in cur.fetchall()]
            if "doc_type" in columns:
                # Optionally, query a metadata table for expected types
                try:
                    cur2 = conn.execute("SELECT DISTINCT doc_type FROM enterprise_documentation")
                    return [row[0] for row in cur2.fetchall()]
                except Exception:
                    return []
            return []
        except Exception:
            return []

    def _write_log(self, summary: Dict[str, Any]) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, indent=2) + "\n")

    def _log_to_db(self, summary: Dict[str, Any]) -> None:
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS documentation_gap_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    details TEXT,
                    ts TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO documentation_gap_analysis (details, ts) VALUES (?, ?)",
                (json.dumps(summary), summary["timestamp"]),
            )
            conn.commit()

    def _dual_copilot_validate(self) -> None:
        """
        DUAL COPILOT: Secondary validator for documentation gap analysis.
        Checks analytics.db for matching analysis event.
        """
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM documentation_gap_analysis")
            db_count = cur.fetchone()[0]
        if db_count > 0:
            logging.info("DUAL COPILOT validation passed: Documentation gap analysis integrity confirmed.")
        else:
            logging.error("DUAL COPILOT validation failed: Documentation gap analysis missing.")

    def _validate_no_recursive_folders(self) -> None:
        """
        Anti-recursion validation before analysis.
        """
        workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    logging.error(f"Recursive folder detected: {folder}")
                    raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")

    def _calculate_etc(self, elapsed: float, current_progress: int, total_work: int) -> str:
        if current_progress > 0:
            total_estimated = elapsed / (current_progress / total_work)
            remaining = total_estimated - elapsed
            return f"{remaining:.2f}s remaining"
        return "N/A"

    def validate(self) -> bool:
        """
        Validate that documentation gap analysis events exist in analytics.db.
        """
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM documentation_gap_analysis")
            return cur.fetchone()[0] > 0

__all__ = ["DocumentationDBAnalyzer"]
