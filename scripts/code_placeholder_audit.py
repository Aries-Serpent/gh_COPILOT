"""
Enterprise Database-First Code Audit Script

MANDATORY REQUIREMENTS:
1. Query production.db for tracked file patterns and audit templates.
2. Traverse all files, extract line number, context, and type.
3. Log each finding to analytics.db.todo_fixme_tracking with file path, line number, context, timestamp.
4. Update /dashboard/compliance with removal status and compliance metrics.
5. Include tqdm progress bar, start time logging, timeout, ETC calculation, anti-recursion validation.
6. DUAL COPILOT: Secondary validator checks audit completeness and compliance.
7. Integrate best practices from deep web research for codebase audits.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from tqdm import tqdm
except ModuleNotFoundError:  # pragma: no cover - fallback
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    from tqdm import tqdm

from scripts.continuous_operation_orchestrator import (
    validate_enterprise_operation,
)
from scripts.database.add_code_audit_log import ensure_code_audit_log
from template_engine.template_placeholder_remover import remove_unused_placeholders
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from utils.log_utils import log_message

# Visual processing indicator constants
TEXT = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "progress": "[PROGRESS]",
    "validate": "[VALIDATE]",
    "complete": "[COMPLETE]",
}

DEFAULT_PATTERNS = [
    r"TODO",
    r"FIXME",
    r"pass\b",
    r"NotImplementedError",
    r"placeholder",
    r"HACK",
    r"BUG",
    r"XXX",
]


def load_best_practice_patterns(config_path: Path | None = None) -> List[str]:
    """Load additional patterns from config/audit_patterns.json if present."""
    cfg = config_path or Path("config/audit_patterns.json")
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            return [str(p) for p in data.get("patterns", [])]
        except Exception as exc:  # pragma: no cover - config errors
            log_message(__name__, f"{TEXT['error']} pattern load failed: {exc}")
    return []


# Database-first: fetch placeholder patterns from production.db
def fetch_db_placeholders(production_db: Path) -> List[str]:
    """Fetch placeholder patterns from production.db for audit."""
    if not production_db.exists():
        return []
    with sqlite3.connect(production_db) as conn:
        try:
            cur = conn.execute("SELECT placeholder_name FROM template_placeholders")
            return [row[0] for row in cur.fetchall()]
        except Exception as e:
            log_message(
                __name__,
                f"{TEXT['error']} Failed to fetch placeholders from production.db: {e}",
                level=logging.ERROR,
            )
            return []


# Insert findings into analytics.db.code_audit_log
def log_findings(
    results: List[Dict],
    analytics_db: Path,
    simulate: bool = False,
    *,
    update_resolutions: bool = False,
) -> None:
    """Log audit results to analytics.db.

    Parameters
    ----------
    results : List[Dict]
        Findings collected from the codebase scan.
    analytics_db : Path
        Target analytics database path.
    simulate : bool, optional
        If True, no database writes occur.

    Returns
    -------
    None
        The function writes to the database when not in simulation mode.
    """
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_code_audit_log(analytics_db)
    # Ensure the tracking table exists even when running in simulation mode so
    # that downstream validation does not fail when querying it.
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0,
                resolved_timestamp DATETIME,
                status TEXT DEFAULT 'open',
                removal_id INTEGER
            )
            """
        )
        conn.commit()
    if simulate:
        log_message(
            __name__,
            "[TEST MODE] Simulation enabled: not writing to analytics.db",
        )
        return
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS code_audit_log (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_code_audit_log_file_path ON code_audit_log(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_code_audit_log_timestamp ON code_audit_log(timestamp)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0,
                resolved_timestamp DATETIME,
                status TEXT DEFAULT 'open',
                removal_id INTEGER
            )
            """
        )
        result_keys = {(r["file"], r["line"], r["pattern"], r["context"]) for r in results}
        cur = conn.execute(
            "SELECT rowid, file_path, line_number, placeholder_type, context FROM todo_fixme_tracking WHERE resolved=0"
        )
        for rowid, fpath, line, ptype, ctx in cur.fetchall():
            if (fpath, line, ptype, ctx) not in result_keys:
                conn.execute(
                    "UPDATE todo_fixme_tracking SET resolved=1, resolved_timestamp=?, status='resolved' WHERE rowid=?",
                    (datetime.now().isoformat(), rowid),
                )
        if not update_resolutions:
            for row in results:
                key = (row["file"], row["line"], row["pattern"], row["context"])
                cur = conn.execute(
                    "SELECT 1 FROM todo_fixme_tracking WHERE file_path=? AND line_number=? AND placeholder_type=? AND context=? AND resolved=0",
                    key,
                )
                if not cur.fetchone():
                    values = (
                        row["file"],
                        row["line"],
                        row["pattern"],
                        row["context"],
                        datetime.now().isoformat(),
                    )
                    conn.execute(
                        "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp)"
                        " VALUES (?, ?, ?, ?, ?)",
                        values,
                    )
                    conn.execute(
                        "INSERT INTO todo_fixme_tracking (file_path, line_number, placeholder_type, context, timestamp, status)"
                        " VALUES (?, ?, ?, ?, ?, 'open')",
                        values,
                    )
        conn.commit()


# Update dashboard/compliance with summary JSON
def update_dashboard(count: int, dashboard_dir: Path, analytics_db: Path) -> None:
    """Write summary JSON to dashboard/compliance directory."""
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    open_count = count
    resolved = 0
    if analytics_db.exists():
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='open'")
            open_count = cur.fetchone()[0]
            cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='resolved'")
            resolved = cur.fetchone()[0]
    compliance = max(0, 100 - open_count)
    status = "complete" if open_count == 0 else "issues_pending"
    data = {
        "timestamp": datetime.now().isoformat(),
        "findings": open_count,
        "resolved_count": resolved,
        "compliance_score": compliance,
        "progress_status": status,
    }
    summary_file = dashboard_dir / "placeholder_summary.json"
    summary_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Scan files for patterns with timeout and visual indicators
def scan_files(workspace: Path, patterns: List[str], timeout: Optional[float] = None) -> List[Dict]:
    """Scan files for given patterns with optional timeout and progress bar."""
    results: List[Dict] = []
    files = [f for f in workspace.rglob("*") if f.is_file()]
    start = time.time()
    with tqdm(total=len(files), desc=f"{TEXT['progress']} scanning", unit="file") as bar:
        for file in files:
            if timeout and time.time() - start > timeout:
                bar.write(f"{TEXT['error']} timeout reached")
                break
            try:
                lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception as e:
                log_message(
                    __name__,
                    f"{TEXT['error']} Could not read {file}: {e}",
                    level=logging.ERROR,
                )
                bar.update(1)
                continue
            for idx, line in enumerate(lines, 1):
                for pat in patterns:
                    if re.search(pat, line):
                        results.append(
                            {
                                "file": str(file),
                                "line": idx,
                                "pattern": pat,
                                "context": line.strip()[:200],
                            }
                        )
            bar.update(1)
    return results


# DUAL COPILOT: Secondary validator for audit completeness
def validate_results(expected_count: int, analytics_db: Path) -> bool:
    """Secondary validation step for dual copilot pattern."""
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking")
        db_count = cur.fetchone()[0]
    return db_count >= expected_count


def rollback_last_entry(db_path: Path) -> bool:
    """Remove the most recent placeholder audit entry from the databases."""
    if not db_path.exists():
        return False
    removed = False
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT rowid FROM todo_fixme_tracking ORDER BY rowid DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            conn.execute("DELETE FROM todo_fixme_tracking WHERE rowid = ?", (row[0],))
            conn.execute(
                "DELETE FROM code_audit_log WHERE rowid = ("
                "SELECT rowid FROM code_audit_log ORDER BY rowid DESC LIMIT 1)"
            )
            conn.commit()
            removed = True
    return removed


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    """Calculate estimated time to completion."""
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


def auto_remove_placeholders(
    results: List[Dict],
    production_db: Path,
    analytics_db: Path,
) -> None:
    """Remove detected placeholders and log corrections."""
    by_file: Dict[str, List[Dict]] = {}
    for res in results:
        by_file.setdefault(res["file"], []).append(res)

    logger = CorrectionLoggerRollback(analytics_db)
    for file_path, file_results in by_file.items():
        path = Path(file_path)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for res in file_results:
            idx = res["line"] - 1
            if 0 <= idx < len(lines):
                lines[idx] = re.sub(r"#\s*(TODO|FIXME).*", "", lines[idx])
        new_text = "\n".join(lines)
        new_text = remove_unused_placeholders(new_text, production_db, analytics_db, timeout_minutes=1)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            logger.log_change(path, "Auto placeholder cleanup", 1.0)

    logger.summarize_corrections()
    # Mark resolved placeholders
    log_findings([], analytics_db, simulate=False, update_resolutions=True)


def main(
    workspace_path: Optional[str] = None,
    analytics_db: Optional[str] = None,
    production_db: Optional[str] = None,
    dashboard_dir: Optional[str] = None,
    timeout_minutes: int = 30,
    simulate: bool = False,
    *,
    exclude_dirs: Optional[List[str]] = None,
    update_resolutions: bool = False,
    apply_fixes: bool = False,
) -> bool:
    """Entry point for placeholder auditing with full enterprise compliance.

    Parameters
    ----------
    simulate:
        If ``True``, skip writing to databases and dashboard.
    apply_fixes:
        When ``True`` automatically remove flagged placeholders and log
        corrections.
    """
    # Visual processing indicators: start time, process ID, anti-recursion validation
    if os.getenv("GH_COPILOT_TEST_MODE") == "1":
        simulate = True
        update_resolutions = True
        log_message(__name__, "[TEST MODE] Simulation enabled")

    start_time = time.time()
    process_id = os.getpid()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log_message(__name__, f"{TEXT['start']} auditing workspace")
    log_message(__name__, f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(__name__, f"Process ID: {process_id}")

    # Anti-recursion validation
    if os.getenv("GH_COPILOT_DISABLE_VALIDATION") != "1":
        validate_enterprise_operation()

    workspace = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics = Path(analytics_db or workspace / "databases" / "analytics.db")
    production = Path(production_db or workspace / "databases" / "production.db")
    dashboard = Path(dashboard_dir or workspace / "dashboard" / "compliance")

    # Database-first: fetch patterns from production.db and config
    patterns = DEFAULT_PATTERNS + fetch_db_placeholders(production) + load_best_practice_patterns()
    timeout = timeout_minutes * 60 if timeout_minutes else None

    # Scan files with progress bar and ETC calculation
    exclude_list = [] if exclude_dirs is None else exclude_dirs
    exclude = {workspace / d for d in exclude_list}
    files = [f for f in workspace.rglob("*") if f.is_file() and not any(str(f).startswith(str(p)) for p in exclude)]
    results: List[Dict] = []
    with tqdm(total=len(files), desc=f"{TEXT['progress']} scanning", unit="file") as bar:
        for idx, file in enumerate(files, 1):
            if timeout and time.time() - start_time > timeout:
                bar.write(f"{TEXT['error']} timeout reached")
                break
            try:
                lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception as e:
                log_message(
                    __name__,
                    f"{TEXT['error']} Could not read {file}: {e}",
                    level=logging.ERROR,
                )
                bar.update(1)
                continue
            for line_num, line in enumerate(lines, 1):
                for pat in patterns:
                    if re.search(pat, line):
                        results.append(
                            {
                                "file": str(file),
                                "line": line_num,
                                "pattern": pat,
                                "context": line.strip()[:200],
                            }
                        )
            elapsed = time.time() - start_time
            etc = calculate_etc(start_time, idx, len(files))
            bar.set_postfix(ETC=etc)
            bar.update(1)

    # Log findings to analytics.db
    log_findings(results, analytics, simulate=simulate, update_resolutions=update_resolutions)
    if apply_fixes and not simulate:
        auto_remove_placeholders(results, production, analytics)
    # Update dashboard/compliance
    if not simulate:
        update_dashboard(len(results), dashboard, analytics)
    else:
        log_message(__name__, "[TEST MODE] Dashboard update skipped")
    elapsed = time.time() - start_time
    log_message(__name__, f"{TEXT['info']} audit completed in {elapsed:.2f}s")

    # DUAL COPILOT validation
    valid = validate_results(len(results), analytics)
    if valid:
        log_message(__name__, f"{TEXT['success']} audit logged {len(results)} findings")
    else:
        log_message(
            __name__,
            f"{TEXT['error']} validation mismatch",
            level=logging.ERROR,
        )
    return valid


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audit workspace for TODO/FIXME placeholders")
    parser.add_argument("--workspace-path", type=str, help="Workspace to scan")
    parser.add_argument("--analytics-db", type=str, help="analytics.db location")
    parser.add_argument("--production-db", type=str, help="production.db location")
    parser.add_argument("--dashboard-dir", type=str, help="dashboard/compliance directory")
    parser.add_argument("--timeout-minutes", type=int, default=30, help="Scan timeout in minutes")
    parser.add_argument("--simulate", action="store_true", help="Run in test mode without writes")
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable test mode (sets GH_COPILOT_TEST_MODE=1 and skips DB writes)",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        dest="exclude_dirs",
        default=None,
        help="Directory to exclude from scanning (can be used multiple times)",
    )
    parser.add_argument(
        "--update-resolutions",
        action="store_true",
        help="Only mark resolved entries; do not log new placeholders",
    )
    parser.add_argument(
        "--apply-fixes",
        action="store_true",
        help="Automatically remove placeholders and log corrections",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove placeholders and log corrections (deprecated: --apply-fixes)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without modifying files or databases",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force cleanup when not in dry-run mode",
    )
    parser.add_argument(
        "--rollback-last",
        action="store_true",
        help="Rollback the most recent audit entry",
    )
    args = parser.parse_args()
    if args.rollback_last:
        result = rollback_last_entry(Path(args.analytics_db or Path.cwd() / "databases" / "analytics.db"))
        print(json.dumps({"rollback": result}))
        raise SystemExit(0 if result else 1)
    if args.test_mode:
        os.environ["GH_COPILOT_TEST_MODE"] = "1"
        args.simulate = True
    if args.cleanup and not (args.dry_run or args.force or args.apply_fixes):
        print(json.dumps({"error": "--cleanup requires --force when not in dry-run"}))
        raise SystemExit(1)
    success = main(
        workspace_path=args.workspace_path,
        analytics_db=args.analytics_db,
        production_db=args.production_db,
        dashboard_dir=args.dashboard_dir,
        timeout_minutes=args.timeout_minutes,
        simulate=args.simulate or args.dry_run,
        exclude_dirs=args.exclude_dirs,
        update_resolutions=args.update_resolutions,
        apply_fixes=args.apply_fixes or args.cleanup,
    )
    summary = {
        "cleanup": bool(args.apply_fixes or args.cleanup),
        "dry_run": bool(args.dry_run or args.simulate),
        "success": success,
    }
    print(json.dumps(summary))
    raise SystemExit(0 if success else 1)
