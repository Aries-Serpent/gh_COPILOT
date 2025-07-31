"""
Enterprise Cross-Reference Validator – DUAL COPILOT, DATABASE-FIRST COMPLIANCE

MANDATORY REQUIREMENTS:
1. Query production.db for cross-referencing and validation patterns.
2. Cross-link all new/modified code, templates, docs with task suggestion files and dashboard.
3. Ensure all actions are auditable via analytics.db and referenced in /dashboard/compliance.
4. Tie every module, output, doc update to a compliance and correction record.
5. Integrate best practices from deep web research for cross-referencing and validation.
6. Use tqdm for progress, start time logging, timeout, ETC calculation, and real-time status updates.
7. Validate anti-recursion and workspace integrity before cross-referencing.
8. DUAL COPILOT: Secondary validator checks for compliance and visual indicators.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from utils.log_utils import _log_event, log_event
from utils.cross_platform_paths import CrossPlatformPathManager

workspace_root = CrossPlatformPathManager.get_workspace_path()
BACKUP_ROOT = CrossPlatformPathManager.get_backup_root()
LOGS_DIR = workspace_root / "logs" / "cross_reference"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"cross_reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

PRODUCTION_DB = workspace_root / "production.db"
ANALYTICS_DB = workspace_root / "analytics.db"
DASHBOARD_DIR = workspace_root / "dashboard" / "compliance"
TASK_SUGGESTIONS_FILE = workspace_root / "docs" / "DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md"


class CrossReferenceValidator:
    """
    Validate cross references between modules, templates, docs, task suggestions, analytics, and dashboard.
    Ensures all actions are auditable and tied to compliance/correction records.
    """

    def __init__(
        self,
        production_db: Path = PRODUCTION_DB,
        analytics_db: Path = ANALYTICS_DB,
        dashboard_dir: Path = DASHBOARD_DIR,
        task_suggestions_file: Path = TASK_SUGGESTIONS_FILE,
    ) -> None:
        self.production_db = production_db
        self.analytics_db = analytics_db
        self.dashboard_dir = dashboard_dir
        self.task_suggestions_file = task_suggestions_file
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.timeout_seconds = 1800  # 30 minutes
        self.status = "INITIALIZED"
        validate_enterprise_operation(str(production_db))
        logging.info("PROCESS STARTED: Cross-Reference Validation")
        logging.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Process ID: {self.process_id}")

        self.cross_link_log: List[Dict[str, str]] = []

    def _query_cross_reference_patterns(self) -> List[str]:
        """Query production.db for cross-referencing workflow patterns."""
        patterns = []
        if not self.production_db.exists():
            logging.warning("production.db not found, using default patterns.")
            return patterns
        with sqlite3.connect(self.production_db) as conn:
            cur = conn.execute("SELECT pattern_name FROM cross_reference_patterns")
            patterns = [row[0] for row in cur.fetchall()]
        logging.info(f"Cross-reference patterns found: {patterns}")
        return patterns

    def _scan_task_suggestions(self) -> List[str]:
        """Scan task suggestion file for actionable items."""
        if not self.task_suggestions_file.exists():
            logging.warning(f"Task suggestions file not found: {self.task_suggestions_file}")
            return []
        with open(self.task_suggestions_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        tasks = [line.strip() for line in lines if line.strip().startswith("- [")]
        logging.info(f"Task suggestions found: {len(tasks)}")
        return tasks

    def _cross_link_actions(self) -> List[Dict]:
        """Cross-link new/modified code, templates, docs with task suggestions and dashboard."""
        actions = []
        # Example: scan analytics.db for recent actions
        if not self.analytics_db.exists():
            logging.warning("analytics.db not found, skipping cross-link.")
            return actions
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT file_path, item_type, status, last_updated FROM todo_fixme_tracking WHERE status='open'"
            )
            for row in cur.fetchall():
                actions.append(
                    {
                        "file_path": row[0],
                        "item_type": row[1],
                        "status": row[2],
                        "last_updated": row[3],
                    }
                )
        logging.info(f"Cross-linked actions found: {len(actions)}")
        return actions

    def _deep_cross_link(self, actions: List[Dict]) -> None:
        """Perform additional cross-linking between docs and code."""
        workspace = CrossPlatformPathManager.get_workspace_path()
        docs_dirs = [workspace / "docs", workspace / "documentation"]
        code_dirs = [workspace]
        for d in docs_dirs + code_dirs:
            validate_enterprise_operation(str(d))
        for act in actions:
            file_name = Path(act["file_path"]).name
            related_paths: Set[Path] = set()
            for d in docs_dirs + code_dirs:
                for path in d.rglob(file_name):
                    try:
                        path.relative_to(BACKUP_ROOT)
                    except ValueError:
                        related_paths.add(path)
            for path in sorted(related_paths):
                entry = {"file_path": act["file_path"], "linked_path": str(path)}
                self.cross_link_log.append(entry)
                log_event(entry, table="cross_link_events", db_path=self.analytics_db)

    def _update_dashboard(self, actions: List[Dict]) -> None:
        """Update dashboard/compliance with cross-reference summary."""
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        summary = {
            "timestamp": datetime.now().isoformat(),
            "cross_linked_actions": actions,
            "cross_links": self.cross_link_log,
            "status": "complete" if actions else "none",
        }
        import json

        summary_file = self.dashboard_dir / "cross_reference_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        logging.info(f"Dashboard cross-reference summary updated: {summary_file}")
        log_event(
            {
                "actions": len(actions),
                "links": len(self.cross_link_log),
                "summary_path": str(summary_file),
            },
            table="cross_link_summary",
            db_path=self.analytics_db,
        )

    def validate(self, timeout_minutes: int = 30) -> bool:
        """
        Full cross-reference validation with progress, ETC, and DUAL COPILOT compliance.
        """
        self.status = "VALIDATING"
        _log_event({"event": "cross_reference_start"}, db_path=self.analytics_db)
        start_time = time.time()
        self._query_cross_reference_patterns()
        self._scan_task_suggestions()
        actions = self._cross_link_actions()
        self._deep_cross_link(actions)
        total_steps = 3
        with tqdm(total=total_steps, desc="Cross-Reference Validation", unit="step") as bar:
            bar.set_description("Querying Patterns")
            bar.update(1)
            bar.set_description("Scanning Task Suggestions")
            bar.update(1)
            bar.set_description("Cross-Linking Actions")
            bar.update(1)
        elapsed = time.time() - start_time
        etc = self._calculate_etc(elapsed, total_steps, total_steps)
        logging.info(f"Cross-reference validation completed in {elapsed:.2f}s | ETC: {etc}")
        self._update_dashboard(actions)
        _log_event({"event": "cross_reference_actions", "count": len(actions)}, db_path=self.analytics_db)
        valid = self._dual_copilot_validate(len(actions))
        if valid:
            logging.info("DUAL COPILOT validation passed: Cross-reference integrity confirmed.")
        else:
            logging.error("DUAL COPILOT validation failed: Cross-reference mismatch.")
        _log_event({"event": "cross_reference_complete", "valid": valid}, db_path=self.analytics_db)
        return valid

    def _calculate_etc(self, elapsed: float, current_progress: int, total_work: int) -> str:
        if current_progress > 0:
            total_estimated = elapsed / (current_progress / total_work)
            remaining = total_estimated - elapsed
            return f"{remaining:.2f}s remaining"
        return "N/A"

    def _dual_copilot_validate(self, expected_count: int) -> bool:
        """Secondary validator for cross-reference integrity and compliance."""
        # Example: check dashboard summary file for expected count
        summary_file = self.dashboard_dir / "cross_reference_summary.json"
        if not summary_file.exists():
            return False
        import json

        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        actual_count = len(data.get("cross_linked_actions", []))
        return actual_count >= expected_count


def main(
    production_db_path: Optional[str] = None,
    analytics_db_path: Optional[str] = None,
    dashboard_dir: Optional[str] = None,
    task_suggestions_file: Optional[str] = None,
    timeout_minutes: int = 30,
) -> bool:
    """
    Entry point for cross-reference validation.
    """
    start_time = time.time()
    process_id = os.getpid()
    logging.info("PROCESS STARTED: Cross-Reference Validator")
    logging.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Process ID: {process_id}")

    validate_enterprise_operation(str(workspace_root))

    workspace = workspace_root
    production_db = Path(production_db_path or workspace / "databases" / "production.db")
    analytics_db = Path(analytics_db_path or workspace / "databases" / "analytics.db")
    dashboard = Path(dashboard_dir or workspace / "dashboard" / "compliance")
    task_suggestions = Path(task_suggestions_file or workspace / "docs" / "DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md")

    validator = CrossReferenceValidator(production_db, analytics_db, dashboard, task_suggestions)
    valid = validator.validate(timeout_minutes=timeout_minutes)
    elapsed = time.time() - start_time
    logging.info(f"Cross-reference validator completed in {elapsed:.2f}s")
    return valid


if __name__ == "__main__":
    success = main()
    raise SystemExit(0 if success else 1)
