"""
Enterprise Database-First Code Audit Script

MANDATORY REQUIREMENTS:
1. Query production.db for tracked file patterns and audit templates.
2. Traverse all files, extract line number, context, and type.
3. Log each finding to analytics.db.placeholder_tasks with file path, line number, context, timestamp.
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
import getpass
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm
import shutil

from enterprise_modules.compliance import (
    anti_recursion_guard,
    pid_recursion_guard,
    validate_enterprise_operation,
)
from scripts.database.add_code_audit_log import ensure_code_audit_log

# ``template_engine`` is optional; fall back to a no-op if missing.
try:
    from template_engine.template_placeholder_remover import remove_unused_placeholders
except ModuleNotFoundError:

    def remove_unused_placeholders(template: str, *args, **kwargs) -> str:  # type: ignore[no-redef]
        """Return template unchanged when placeholder remover is unavailable."""
        return template


from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
import secondary_copilot_validator
from utils.log_utils import log_message

try:  # pragma: no cover - optional dependency for dashboard integration
    from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
except Exception:  # pragma: no cover - allow absence during unit tests
    ComplianceMetricsUpdater = None  # type: ignore[assignment]
try:  # pragma: no cover - optional dependency for template generation
    from unified_script_generation_system import EnterpriseUtility
except Exception:  # pragma: no cover - allow absence during unit tests
    EnterpriseUtility = None  # type: ignore[assignment]
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator
from unified_monitoring_optimization_system import collect_metrics, push_metrics
from enterprise_modules.compliance import load_placeholder_patterns

__all__ = [
    "snapshot_placeholder_counts",
    "get_latest_placeholder_snapshot",
]

# Visual processing indicator constants
TEXT = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "warn": "[WARN]",
    "progress": "[PROGRESS]",
    "validate": "[VALIDATE]",
    "complete": "[COMPLETE]",
}

DEFAULT_PATTERNS = load_placeholder_patterns()


def load_best_practice_patterns(
    config_path: Path | None = None, dataset_path: Path | None = None
) -> List[str]:
    """Load patterns from optional config and dataset."""

    patterns: List[str] = []
    if config_path and config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            patterns.extend(str(p) for p in data.get("placeholder_patterns", []))
        except Exception as exc:  # pragma: no cover - config errors
            log_message(__name__, f"{TEXT['error']} pattern load failed: {exc}")

    dataset = dataset_path or Path(os.getenv("GH_COPILOT_PATTERN_DATASET", ""))
    if dataset and dataset.exists():
        try:
            data = json.loads(dataset.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                patterns.extend(str(p) for p in data.get("patterns", []))
            elif isinstance(data, list):
                patterns.extend(str(p) for p in data)
        except Exception as exc:  # pragma: no cover - dataset errors
            log_message(__name__, f"{TEXT['error']} dataset load failed: {exc}")

    return patterns


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


# Generate human-readable tasks for removing placeholders
def generate_removal_tasks(
    results: List[Dict],
    production_db: Path | None = None,
    analytics_db: Path | None = None,
) -> List[Dict[str, str]]:
    """Return structured tasks for each detected placeholder.

    Each task includes the human readable description along with the
    original placeholder metadata so downstream tooling can parse it.

    When database paths are supplied, suggestions are generated by
    processing the context through :func:`remove_unused_placeholders`.
    """

    def _suggest_fix(text: str) -> str:
        """Return a simple suggestion for TODO/FIXME style comments."""

        return re.sub(r"\b(?:TODO|FIXME)\b:?[ ]*", "", text).strip()

    tasks: List[Dict[str, str]] = []
    for item in results:
        description = f"Remove {item['pattern']} in {item['file']}:{item['line']} - {item['context']}"
        suggestion = _suggest_fix(item["context"])
        if production_db and analytics_db:
            try:
                suggestion = remove_unused_placeholders(
                    item["context"],
                    production_db=production_db,
                    analytics_db=analytics_db,
                    timeout_minutes=1,
                    simulate=True,
                )
            except Exception:
                suggestion = item["context"]
        suggestion = _suggest_fix(suggestion)
        tasks.append(
            {
                "task": description,
                "file": item["file"],
                "line": str(item["line"]),
                "pattern": item["pattern"],
                "context": item["context"],
                "suggestion": suggestion.strip(),
            }
        )
    return tasks


def write_tasks_report(tasks: List[Dict[str, str]], report_path: Path) -> None:
    """Write placeholder removal tasks to JSON or Markdown."""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.suffix.lower() == ".md":
        lines = [f"- [ ] {t['task']}" for t in tasks]
        report_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        report_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def log_placeholder_tasks(tasks: List[Dict[str, str]], analytics_db: Path, simulate: bool = False) -> int:
    """Persist placeholder removal tasks to tracking tables.

    Findings are written to both the legacy ``todo_fixme_tracking`` table
    and the newer ``placeholder_tasks`` table. Each entry tracks whether the
    placeholder is ``open`` or ``resolved`` so downstream tooling can derive
    resolution ratios.
    """

    if simulate:
        return 0

    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        _ensure_placeholder_tables(conn)
        # Ensure the suggestion column exists for pre-existing databases.
        cur = conn.execute("PRAGMA table_info(todo_fixme_tracking)")
        cols = {row[1] for row in cur.fetchall()}
        if "suggestion" not in cols:
            conn.execute("ALTER TABLE todo_fixme_tracking ADD COLUMN suggestion TEXT")
        author = os.getenv("GH_COPILOT_USER", getpass.getuser())
        tasks_inserted = 0
        for task in tasks:
            key = (task["file"], int(task["line"]), task["pattern"], task["context"])

            # Insert/update placeholder_tasks table
            cur = conn.execute(
                "SELECT rowid FROM placeholder_tasks WHERE file_path=? AND line_number=? AND pattern=? AND context=?",
                key,
            )
            row = cur.fetchone()
            if row:
                conn.execute(
                    "UPDATE placeholder_tasks SET suggestion=?, status='open', resolved=0 WHERE rowid=?",
                    (task["suggestion"], row[0]),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO placeholder_tasks (
                        file_path, line_number, pattern, context,
                        suggestion, timestamp, author, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
                    """,
                    (
                        task["file"],
                        int(task["line"]),
                        task["pattern"],
                        task["context"],
                        task["suggestion"],
                        datetime.now().isoformat(),
                        author,
                    ),
                )
                tasks_inserted += 1

            # Mirror entry in legacy todo_fixme_tracking table
            cur = conn.execute(
                "SELECT rowid FROM todo_fixme_tracking WHERE file_path=? AND line_number=? AND placeholder_type=? AND context=?",
                key,
            )
            row = cur.fetchone()
            if row:
                conn.execute(
                    "UPDATE todo_fixme_tracking SET suggestion=?, status='open', resolved=0 WHERE rowid=?",
                    (task["suggestion"], row[0]),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO todo_fixme_tracking (
                        file_path, line_number, placeholder_type, context,
                        suggestion, timestamp, author, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
                    """,
                    (
                        task["file"],
                        int(task["line"]),
                        task["pattern"],
                        task["context"],
                        task["suggestion"],
                        datetime.now().isoformat(),
                        author,
                    ),
                )
        conn.commit()
        # Record snapshot and metrics
        open_count = conn.execute("SELECT COUNT(*) FROM placeholder_tasks WHERE status='open'").fetchone()[0]
        resolved_count = conn.execute("SELECT COUNT(*) FROM placeholder_tasks WHERE status='resolved'").fetchone()[0]
        try:
            auto_removal_count = conn.execute(
                "SELECT COUNT(*) FROM corrections WHERE rationale='Auto placeholder cleanup'"
            ).fetchone()[0]
        except sqlite3.Error:
            auto_removal_count = 0
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS placeholder_metrics (
                timestamp TEXT,
                open_placeholders INTEGER,
                resolved_placeholders INTEGER,
                compliance_score REAL,
                progress REAL,
                auto_removal_count INTEGER
            )
            """
        )
        denom = open_count + resolved_count
        compliance = resolved_count / denom if denom else 1.0
        conn.execute(
            "INSERT INTO placeholder_metrics VALUES (?,?,?,?,?,?)",
            (
                datetime.now().isoformat(),
                open_count,
                resolved_count,
                compliance * 100,
                compliance,
                auto_removal_count,
            ),
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots(timestamp, open_count, resolved_count) VALUES (?,?,?)",
            (int(time.time()), open_count, resolved_count),
        )
        conn.commit()
    return tasks_inserted


def verify_task_completion(analytics_db: Path, workspace: Path) -> int:
    """Mark tasks as resolved when placeholders disappear from files.

    Parameters
    ----------
    analytics_db:
        Path to ``analytics.db`` containing the tracking table.
    workspace:
        Workspace root used to ensure files remain under the project tree.

    Returns
    -------
    int
        Number of tasks marked as resolved.
    """

    if not analytics_db.exists():
        return 0

    resolved = 0
    with sqlite3.connect(analytics_db) as conn:
        tables = []
        if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='placeholder_tasks'").fetchone():
            tables.append(("placeholder_tasks", "pattern"))
        if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todo_fixme_tracking'").fetchone():
            tables.append(("todo_fixme_tracking", "placeholder_type"))

        for table, col in tables:
            cur = conn.execute(f"SELECT rowid, file_path, line_number, {col} FROM {table} WHERE status='open'")
            rows = cur.fetchall()
            for rowid, fpath, line, pattern in rows:
                path = Path(fpath)
                try:
                    if not path.resolve().is_relative_to(workspace.resolve()):
                        continue
                except Exception:
                    try:
                        if not str(path.resolve()).startswith(str(workspace.resolve())):
                            continue
                    except Exception:
                        continue
                if not path.exists():
                    continue
                try:
                    content = path.read_text(encoding="utf-8").splitlines()
                except Exception:
                    continue
                if 1 <= int(line) <= len(content):
                    if not re.search(pattern, content[int(line) - 1]):
                        conn.execute(
                            f"UPDATE {table} SET resolved=1, status='resolved', resolved_timestamp=? WHERE rowid=?",
                            (datetime.now().isoformat(), rowid),
                        )
                        resolved += 1
        conn.commit()
    return resolved


# ---------------------------------------------------------------------------
# Placeholder snapshot utilities
# ---------------------------------------------------------------------------


def _ensure_placeholder_tables(conn: sqlite3.Connection) -> None:
    """Create placeholder audit tables if they do not exist."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS placeholder_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            line_number INTEGER,
            placeholder_type TEXT,
            context TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS placeholder_audit_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            open_count INTEGER NOT NULL,
            resolved_count INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS placeholder_tasks (
            file_path TEXT,
            line_number INTEGER,
            pattern TEXT,
            context TEXT,
            suggestion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            author TEXT,
            resolved BOOLEAN DEFAULT 0,
            resolved_timestamp DATETIME,
            resolved_by TEXT,
            status TEXT DEFAULT 'open'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
            file_path TEXT,
            line_number INTEGER,
            placeholder_type TEXT,
            context TEXT,
            suggestion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            author TEXT,
            resolved BOOLEAN DEFAULT 0,
            resolved_timestamp DATETIME,
            resolved_by TEXT,
            status TEXT DEFAULT 'open',
            removal_id INTEGER
        )
        """
    )


def record_unresolved_placeholders(
    results: List[Dict[str, str]],
    analytics_db: Path,
) -> None:
    """Record unresolved placeholder findings to ``analytics_db``.

    Creates the ``unresolved_placeholders`` table with a unique index on
    ``(file, line)`` and inserts each result using ``INSERT OR IGNORE`` to
    suppress duplicates.
    """

    rows = [(r["file"], int(r["line"]), r.get("pattern", ""), r.get("context", "")) for r in results]
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS unresolved_placeholders (
                file TEXT,
                line INTEGER,
                pattern TEXT,
                context TEXT
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_unresolved_file_line ON unresolved_placeholders(file, line)"
        )
        conn.executemany(
            "INSERT OR IGNORE INTO unresolved_placeholders (file, line, pattern, context) VALUES (?, ?, ?, ?)",
            rows,
        )
        conn.commit()


def snapshot_placeholder_counts(db: Path) -> Tuple[int, int]:
    """Aggregate open and resolved placeholder counts.

    Parameters
    ----------
    db:
        Path to ``analytics.db``.

    Returns
    -------
    Tuple[int, int]
        The open and resolved counts respectively.
    """

    with sqlite3.connect(db) as conn:
        _ensure_placeholder_tables(conn)
        if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='placeholder_tasks'").fetchone():
            cur = conn.execute("SELECT COUNT(*) FROM placeholder_tasks WHERE status='open'")
            open_count = int(cur.fetchone()[0])
            cur = conn.execute("SELECT COUNT(*) FROM placeholder_tasks WHERE status='resolved'")
            resolved_count = int(cur.fetchone()[0])
        else:
            cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='open'")
            open_count = int(cur.fetchone()[0])
            cur = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='resolved'")
            resolved_count = int(cur.fetchone()[0])
        return open_count, resolved_count


def calculate_placeholder_density(db: Path, workspace: Path) -> float:
    """Return open placeholders per 1000 lines of code."""
    open_count, _ = snapshot_placeholder_counts(db)
    loc = 0
    for path in workspace.rglob("*.py"):
        try:
            loc += sum(1 for _ in path.open("r", encoding="utf-8"))
        except OSError:
            continue
    density = (open_count / loc * 1000) if loc else 0.0
    with sqlite3.connect(db) as conn:
        _ensure_placeholder_tables(conn)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS placeholder_density (ts TEXT, density REAL)"
        )
        conn.execute(
            "INSERT INTO placeholder_density (ts, density) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), density),
        )
        # Mirror density to todo_fixme_tracking for historical tracking
        conn.execute(
            "DELETE FROM todo_fixme_tracking WHERE file_path='__metrics__' AND placeholder_type='density'",
        )
        conn.execute(
            """
            INSERT INTO todo_fixme_tracking (
                file_path, line_number, placeholder_type, context, timestamp, status
            ) VALUES (?, ?, ?, ?, ?, 'open')
            """,
            (
                "__metrics__",
                0,
                "density",
                f"{density}",
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    push_metrics({"placeholder_density": density}, db_path=db)
    if density > 5:
        logging.warning("Placeholder density %.2f exceeds threshold", density)
    return density


def get_latest_placeholder_snapshot(
    conn: sqlite3.Connection,
) -> Tuple[int, int]:
    """Return the most recent open/resolved counts.

    Parameters
    ----------
    conn:
        SQLite connection to ``analytics.db``.

    Returns
    -------
    Tuple[int, int]
        ``(open, resolved)`` counts. Returns ``(0, 0)`` when no snapshot
        exists.
    """

    _ensure_placeholder_tables(conn)
    cur = conn.execute("SELECT open_count, resolved_count FROM placeholder_audit_snapshots ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    return (int(row[0]), int(row[1])) if row else (0, 0)


# Insert findings into analytics.db.code_audit_log
def log_findings(
    results: List[Dict],
    analytics_db: Path,
    simulate: bool = False,
    *,
    update_resolutions: bool = False,
    auto_remove_resolved: bool = False,
) -> int:
    """Log audit results to analytics.db.

    Parameters
    ----------
    results : List[Dict]
        Findings collected from the codebase scan.
    analytics_db : Path
        Target analytics database path.
    simulate : bool, optional
        If True, no database writes occur.
    auto_remove_resolved : bool, optional
        When ``True`` delete entries marked as resolved from the tracking table.

    Returns
    -------
    int
        Number of newly inserted audit records.
    """
    user = os.getenv("USER", "system")
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
                suggestion TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                author TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolved_timestamp DATETIME,
                resolved_by TEXT,
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
        return 0
    findings_inserted = 0
    with sqlite3.connect(analytics_db) as conn:
        _ensure_placeholder_tables(conn)
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS code_audit_history (
                id INTEGER PRIMARY KEY,
                audit_entry TEXT NOT NULL,
                user TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_code_audit_log_file_path ON code_audit_log(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_code_audit_log_timestamp ON code_audit_log(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_code_audit_history_timestamp ON code_audit_history(timestamp)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                suggestion TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                author TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolved_timestamp DATETIME,
                resolved_by TEXT,
                status TEXT DEFAULT 'open',
                removal_id INTEGER
            )
            """
        )
        result_keys = {(r["file"], r["line"], r["pattern"], r["context"]) for r in results}
        author = os.getenv("GH_COPILOT_USER", getpass.getuser())
        cur = conn.execute(
            "SELECT rowid, file_path, line_number, placeholder_type, context FROM todo_fixme_tracking WHERE resolved=0"
        )
        for rowid, fpath, line, ptype, ctx in cur.fetchall():
            if (fpath, line, ptype, ctx) not in result_keys:
                conn.execute(
                    "UPDATE todo_fixme_tracking SET resolved=1, resolved_timestamp=?, resolved_by=?, status='resolved' WHERE rowid=?",
                    (datetime.now().isoformat(), author, rowid),
                )
        cur = conn.execute(
            "SELECT rowid, file_path, line_number, pattern, context FROM placeholder_tasks WHERE resolved=0"
        )
        for rowid, fpath, line, ptype, ctx in cur.fetchall():
            if (fpath, line, ptype, ctx) not in result_keys:
                conn.execute(
                    "UPDATE placeholder_tasks SET resolved=1, resolved_timestamp=?, resolved_by=?, status='resolved' WHERE rowid=?",
                    (datetime.now().isoformat(), author, rowid),
                )
        if auto_remove_resolved:
            conn.execute("DELETE FROM todo_fixme_tracking WHERE resolved=1")
            conn.execute("DELETE FROM placeholder_tasks WHERE resolved=1")
        if not update_resolutions:
            for row in results:
                key = (row["file"], row["line"], row["pattern"], row["context"])
                cur = conn.execute(
                    "SELECT 1 FROM placeholder_tasks WHERE file_path=? AND line_number=? AND pattern=? AND context=? AND resolved=0",
                    key,
                )
                if not cur.fetchone():
                    conn.execute(
                        """
                        INSERT INTO placeholder_tasks (
                            file_path, line_number, pattern, context, suggestion,
                            timestamp, author, status
                        ) VALUES (?, ?, ?, ?, '', ?, ?, 'open')
                        """,
                        (
                            row["file"],
                            row["line"],
                            row["pattern"],
                            row["context"],
                            datetime.now().isoformat(),
                            author,
                        ),
                    )
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
                        author,
                    )
                    conn.execute(
                        "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp)"
                        " VALUES (?, ?, ?, ?, ?)",
                        values[:-1],
                    )
                    conn.execute(
                        "INSERT INTO placeholder_audit (file_path, line_number, placeholder_type, context, timestamp)"
                        " VALUES (?, ?, ?, ?, ?)",
                        values[:-1],
                    )
                    conn.execute(
                        "INSERT INTO code_audit_history (audit_entry, user, timestamp) VALUES (?, ?, ?)",
                        (
                            f"audit:{row['file']}:{row['line']}",
                            user,
                            datetime.now().isoformat(),
                        ),
                    )
                    conn.execute(
                        "INSERT INTO todo_fixme_tracking (file_path, line_number, placeholder_type, context, timestamp, status)"
                        " VALUES (?, ?, ?, ?, ?, 'open')",
                        values[:-1],
                    )
                    findings_inserted += 1
        conn.commit()
    return findings_inserted


def apply_suggestions_to_files(
    tasks: List[Dict[str, str]],
    analytics_db: Path,
    workspace: Path,
    simulate: bool = False,
) -> List[Dict[str, str]]:
    """Apply generated suggestions to source files within ``workspace``.

    Any task whose path resolves outside the provided ``workspace`` is skipped
    and logged. Returns a list of tasks that could not be applied and remain
    unresolved.
    """

    if simulate:
        return tasks
    unresolved: List[Dict[str, str]] = []
    author = os.getenv("GH_COPILOT_USER", getpass.getuser())
    ws_resolved = workspace.resolve()
    for task in tasks:
        suggestion = task.get("suggestion", "").strip()
        if not suggestion or suggestion == task["context"].strip():
            unresolved.append(task)
            continue
        path = Path(task["file"])
        if not path.is_absolute():
            path = ws_resolved / path
        try:
            resolved = path.resolve()
            resolved.relative_to(ws_resolved)
        except Exception:
            log_message(
                __name__,
                f"{TEXT['warn']} skipping outside workspace: {path}",
                level=logging.WARNING,
            )
            unresolved.append(task)
            continue
        try:
            lines = resolved.read_text(encoding="utf-8").splitlines()
        except Exception:
            unresolved.append(task)
            continue
        idx = int(task["line"]) - 1
        if 0 <= idx < len(lines):
            with sqlite3.connect(analytics_db) as conn:
                cur = conn.execute(
                    "SELECT 1 FROM todo_fixme_tracking WHERE file_path=? AND line_number=? AND placeholder_type=? AND context=?",
                    (
                        task["file"],
                        int(task["line"]),
                        task["pattern"],
                        task["context"],
                    ),
                )
                if cur.fetchone():
                    lines[idx] = suggestion
                    resolved.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    conn.execute(
                        "UPDATE todo_fixme_tracking SET resolved=1, resolved_timestamp=?, resolved_by=?, status='resolved' WHERE file_path=? AND line_number=? AND placeholder_type=? AND context=?",
                        (
                            datetime.now().isoformat(),
                            author,
                            task["file"],
                            int(task["line"]),
                            task["pattern"],
                            task["context"],
                        ),
                    )
                    conn.commit()
                else:
                    unresolved.append(task)
        else:
            unresolved.append(task)
    return unresolved


# Update dashboard/compliance with summary JSON
def update_dashboard(
    count: int,
    dashboard_dir: Path,
    analytics_db: Path,
    summary_json: Path | None = None,
) -> None:
    """Write summary JSON to ``dashboard/compliance`` directory.

    Parameters
    ----------
    summary_json:
        Optional explicit path for the summary JSON output. Defaults to
        ``dashboard_dir/placeholder_summary.json``.
    """
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    open_count = count
    resolved = 0
    compliance_pct = 0.0
    progress = 0.0
    auto_removal_count = 0
    timestamp = datetime.now().isoformat()
    placeholder_counts: Dict[str, int] = {}
    if analytics_db.exists():
        with sqlite3.connect(analytics_db) as conn:
            try:
                cur = conn.execute(
                    """
                    SELECT timestamp, open_placeholders, resolved_placeholders,
                           compliance_score, progress, auto_removal_count
                    FROM placeholder_metrics ORDER BY timestamp DESC LIMIT 1
                    """
                )
                row = cur.fetchone()
            except sqlite3.Error:
                row = None
            if row:
                timestamp, open_count, resolved, compliance_pct, progress, auto_removal_count = row
            tables = []
            if conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='placeholder_tasks'",
            ).fetchone():
                tables.append(("placeholder_tasks", "pattern"))
            else:
                tables.append(("todo_fixme_tracking", "placeholder_type"))
            for table, col in tables:
                cur = conn.execute(
                    f"SELECT {col}, COUNT(*) FROM {table} WHERE status='open' GROUP BY {col}",
                )
                for ptype, cnt in cur.fetchall():
                    placeholder_counts[ptype] = placeholder_counts.get(ptype, 0) + cnt

    status = "complete" if open_count == 0 else "issues_pending"
    compliance_status = "compliant" if open_count == 0 else "non_compliant"
    data = {
        "timestamp": timestamp,
        "findings": open_count,
        "resolved_count": resolved,
        "compliance_score": compliance_pct,
        "progress": progress,
        "progress_status": status,
        "compliance_status": compliance_status,
        "placeholder_counts": placeholder_counts,
        "auto_removal_count": auto_removal_count,
    }
    path = summary_json or dashboard_dir / "placeholder_summary.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    dashboard_metrics = {
        "open_placeholders": open_count,
        "resolved_placeholders": resolved,
        "compliance_score": compliance_pct,
        "progress": progress,
        "auto_removal_count": auto_removal_count,
    }

    metrics_path = dashboard_dir / "metrics.json"
    metrics_payload = {
        "metrics": dashboard_metrics,
        "status": "updated",
        "timestamp": timestamp,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    # Expose counts and history for dashboard widgets
    counts_payload = {
        "open": open_count,
        "resolved": resolved,
        "timestamp": timestamp,
    }
    (dashboard_dir / "placeholder_counts.json").write_text(json.dumps(counts_payload, indent=2), encoding="utf-8")
    history: List[Dict[str, int]] = []
    if analytics_db.exists():
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute(
                "SELECT timestamp, open_count, resolved_count FROM placeholder_audit_snapshots ORDER BY timestamp"
            )
            history = [{"timestamp": row[0], "open_count": row[1], "resolved_count": row[2]} for row in cur.fetchall()]
    (dashboard_dir / "placeholder_history.json").write_text(
        json.dumps({"history": history}, indent=2), encoding="utf-8"
    )


def export_resolved_placeholders(analytics_db: Path, dashboard_dir: Path) -> None:
    """Export resolved placeholders to dashboard/compliance."""

    if not analytics_db.exists():
        return
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT file_path, line_number, placeholder_type, context FROM todo_fixme_tracking WHERE status='resolved'"
        )
        rows = [
            {
                "file": row[0],
                "line": row[1],
                "pattern": row[2],
                "context": row[3],
            }
            for row in cur.fetchall()
        ]
    (dashboard_dir / "resolved_placeholders.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


# Scan a single file for placeholder patterns
def scan_file_for_placeholders(file_path: Path, patterns: List[str] | None = None) -> List[Dict]:
    """Return placeholder findings for ``file_path``.

    Parameters
    ----------
    file_path:
        File to scan for placeholder tokens.
    patterns:
        Optional list of regex patterns. Defaults to :data:`DEFAULT_PATTERNS`.

    Returns
    -------
    List[Dict]
        A list of findings with ``file``, ``line``, ``pattern`` and ``context``
        keys. Errors reading the file are logged and yield an empty list.
    """

    patterns = patterns or DEFAULT_PATTERNS
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as exc:  # pragma: no cover - read errors are logged
        log_message(
            __name__,
            f"{TEXT['error']} Could not read {file_path}: {exc}",
            level=logging.ERROR,
        )
        return []
    results: List[Dict] = []
    for idx, line in enumerate(lines, 1):
        for pat in patterns:
            if re.search(pat, line):
                results.append(
                    {
                        "file": str(file_path),
                        "line": idx,
                        "pattern": pat,
                        "context": line.strip()[:200],
                    }
                )
    return results


# Scan files for patterns with timeout and visual indicators
@pid_recursion_guard
@anti_recursion_guard
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


def rollback_last_entry(db_path: Path, entry_id: int | None = None) -> bool:
    """Remove a placeholder audit entry from the databases."""
    if not db_path.exists():
        return False
    removed = False
    with sqlite3.connect(db_path) as conn:
        if entry_id is None:
            cur = conn.execute("SELECT rowid FROM todo_fixme_tracking ORDER BY rowid DESC LIMIT 1")
            row = cur.fetchone()
            entry_id = row[0] if row else None
        if entry_id is not None:
            conn.execute("DELETE FROM todo_fixme_tracking WHERE rowid = ?", (entry_id,))
            conn.execute(
                "DELETE FROM code_audit_log WHERE rowid = ?",
                (entry_id,),
            )
            conn.commit()
            removed = True
    return removed


def rollback_audit_entry(db_path: Path, entry_id: int) -> bool:
    """Rollback a specific audit entry by rowid."""
    if not db_path.exists():
        return False
    removed = False
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT rowid FROM todo_fixme_tracking WHERE rowid=?",
            (entry_id,),
        )
        row = cur.fetchone()
        if row:
            conn.execute(
                "DELETE FROM todo_fixme_tracking WHERE rowid=?",
                (entry_id,),
            )
            conn.execute(
                "DELETE FROM code_audit_log WHERE rowid=?",
                (entry_id,),
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


def _auto_fill_with_templates(
    target: Path,
    logger: CorrectionLoggerRollback,
    backup_path: Path,
) -> None:
    """Auto-fill missing sections using unified script generation system.

    Parameters
    ----------
    target:
        File path to augment.
    logger:
        ``CorrectionLoggerRollback`` instance for logging changes.
    backup_path:
        Path to backup for potential rollback.
    """
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    if not EnterpriseUtility:
        return
    utility = EnterpriseUtility(str(workspace))
    if utility.perform_utility_function():
        gen_dir = workspace / "generated_templates"
        try:
            latest = max(gen_dir.glob("template_*.txt"), key=lambda p: p.stat().st_mtime)
        except ValueError:
            return
        content = latest.read_text(encoding="utf-8")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n" + content)
        if secondary_copilot_validator.run_flake8([str(target)]):
            logger.log_change(
                target,
                "Auto fill missing sections",
                compliance_score=1.0,
                rollback_reference=str(backup_path),
            )
        else:
            logger.log_change(
                target,
                "Auto fill failed validation",
                compliance_score=0.0,
                rollback_reference=str(backup_path),
            )
            logger.auto_rollback(target, backup_path)


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
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp"))
        backup_dir = backup_root / "auto_placeholder_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{path.name}.{int(time.time())}.bak"
        shutil.copy2(path, backup_path)
        new_text = remove_unused_placeholders(
            new_text,
            production_db,
            analytics_db,
            timeout_minutes=1,
            source_path=path,
            logger=logger,
            backup_path=backup_path,
        )
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            if secondary_copilot_validator.run_flake8([str(path)]):
                logger.log_change(
                    path,
                    "Auto placeholder cleanup",
                    correction_type="placeholder_cleanup",
                    rollback_reference=str(backup_path),
                )
            else:
                logger.log_change(
                    path,
                    "Auto placeholder cleanup failed validation",
                    correction_type="placeholder_cleanup_failed",
                    rollback_reference=str(backup_path),
                )
                logger.auto_rollback(path, backup_path)
            _auto_fill_with_templates(path, logger, backup_path)

    logger.summarize_corrections()
    # Mark resolved placeholders
    log_findings(
        [],
        analytics_db,
        simulate=False,
        update_resolutions=True,
        auto_remove_resolved=False,
    )


def auto_resolve_placeholders(
    tasks: List[Dict[str, str]],
    production_db: Path,
    analytics_db: Path,
) -> None:
    """Resolve placeholders using :func:`remove_unused_placeholders`.

    Each task is logged via ``CorrectionLoggerRollback`` and the corresponding
    entry in ``todo_fixme_tracking`` is marked as resolved.
    """
    logger = CorrectionLoggerRollback(analytics_db)
    author = os.getenv("GH_COPILOT_USER", getpass.getuser())
    for task in tasks:
        path = Path(task["file"])
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        try:
            idx = int(task["line"]) - 1
        except (TypeError, ValueError):
            idx = -1
        if 0 <= idx < len(lines):
            lines[idx] = re.sub(r"#\s*(TODO|FIXME).*", "", lines[idx])
        new_text = "\n".join(lines)
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp"))
        backup_dir = backup_root / "auto_resolve_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{path.name}.{int(time.time())}.bak"
        shutil.copy2(path, backup_path)
        new_text = remove_unused_placeholders(
            new_text,
            production_db,
            analytics_db,
            timeout_minutes=1,
            source_path=path,
            logger=logger,
            backup_path=backup_path,
        )
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
        logger.log_change(
            path,
            task["task"],
            correction_type="placeholder_auto_resolve",
            rollback_reference=str(backup_path),
        )
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "UPDATE todo_fixme_tracking SET resolved=1, resolved_timestamp=?, resolved_by=?, status='resolved' WHERE file_path=? AND line_number=? AND placeholder_type=? AND context=?",
                (
                    datetime.now().isoformat(),
                    author,
                    task["file"],
                    int(task["line"]),
                    task["pattern"],
                    task["context"],
                ),
            )
            conn.commit()
    logger.summarize_corrections()


def main(
    workspace_path: Optional[str] = None,
    analytics_db: Optional[str] = None,
    production_db: Optional[str] = None,
    dashboard_dir: Optional[str] = None,
    dataset_path: Optional[str] = None,
    timeout_minutes: int = 30,
    simulate: bool = False,
    *,
    exclude_dirs: Optional[List[str]] = None,
    update_resolutions: bool = False,
    apply_fixes: bool = False,
    apply_suggestions: bool = False,
    auto_resolve: bool = False,
    export: Optional[Path] = None,
    task_report: Optional[Path] = None,
    summary_json: Optional[str] = None,
    fail_on_findings: bool = False,
) -> bool:
    """Entry point for placeholder auditing with full enterprise compliance.

    Parameters
    ----------
    simulate:
        If ``True``, skip writing to databases and dashboard.
    apply_fixes:
        When ``True`` automatically remove flagged placeholders and log
        corrections.
    dataset_path:
        Optional path to a JSON file containing additional audit patterns.
    summary_json:
        Optional path for ``placeholder_summary.json`` output.
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
    summary_path = Path(summary_json) if summary_json else None

    # Database-first: fetch patterns from production.db and dataset
    patterns = list(
        dict.fromkeys(
            DEFAULT_PATTERNS
            + fetch_db_placeholders(production)
            + load_best_practice_patterns(
                dataset_path=Path(dataset_path) if dataset_path else None
            )
        )
    )
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
    findings_inserted = log_findings(
        results,
        analytics,
        simulate=simulate,
        update_resolutions=update_resolutions,
        auto_remove_resolved=update_resolutions,
    )
    if not simulate:
        log_message(
            __name__,
            f"{TEXT['info']} logged {findings_inserted} findings to {analytics}",
        )
        try:
            metrics = collect_metrics(db_path=Path(":memory:"))
            metrics["placeholder_findings"] = float(findings_inserted)
            push_metrics(metrics, db_path=analytics)
        except Exception as exc:
            log_message(
                __name__,
                f"{TEXT['error']} metrics collection failed: {exc}",
                level=logging.ERROR,
            )
    if export:
        export.write_text(json.dumps(results, indent=2), encoding="utf-8")
    tasks = generate_removal_tasks(results, production, analytics)
    if apply_suggestions and not simulate:
        tasks = apply_suggestions_to_files(tasks, analytics, workspace)
    open_count = resolved_count = 0
    if not simulate:
        tasks_inserted = log_placeholder_tasks(tasks, analytics)
        log_message(
            __name__,
            f"{TEXT['info']} logged {tasks_inserted} tasks to {analytics}",
        )
        try:
            open_count, resolved_count = snapshot_placeholder_counts(analytics)
        except Exception as exc:
            log_message(
                __name__,
                f"{TEXT['error']} snapshot failed: {exc}",
                level=logging.ERROR,
            )
        try:
            from scripts.compliance.update_compliance_metrics import update_compliance_metrics

            update_compliance_metrics(str(workspace))
        except Exception as exc:
            log_message(
                __name__,
                f"{TEXT['error']} compliance metrics update failed: {exc}",
                level=logging.ERROR,
            )
    for task in tasks:
        log_message(__name__, f"[TASK] {task['task']}")
    if task_report:
        write_tasks_report(tasks, task_report)
    if auto_resolve and not simulate:
        auto_resolve_placeholders(tasks, production, analytics)
    elif apply_fixes and not simulate:
        auto_remove_placeholders(results, production, analytics)
    if not simulate:
        verify_task_completion(analytics, workspace)
    secondary_copilot_validator.run_flake8([r["file"] for r in results])
    # Update dashboard/compliance
    if not simulate:
        update_dashboard(len(results), dashboard, analytics, summary_path)
        export_resolved_placeholders(analytics, dashboard)
        try:
            metrics = collect_metrics(db_path=Path(":memory:"))
            metrics["placeholder_open"] = float(open_count)
            metrics["placeholder_resolved"] = float(resolved_count)
            push_metrics(metrics, db_path=analytics)
        except Exception as exc:
            log_message(
                __name__,
                f"{TEXT['error']} metrics collection failed: {exc}",
                level=logging.ERROR,
            )
    else:
        log_message(__name__, "[TEST MODE] Dashboard update skipped")
    # Combine with Compliance Metrics Updater for real-time metrics
    if (not simulate) and ComplianceMetricsUpdater and findings_inserted:
        try:
            updater = ComplianceMetricsUpdater(dashboard, test_mode=simulate)
            updater.update(simulate=simulate)
            updater.validate_update()
        except Exception as exc:  # pragma: no cover - updater errors
            log_message(
                __name__,
                f"{TEXT['error']} compliance update failed: {exc}",
                level=logging.ERROR,
            )
    elapsed = time.time() - start_time
    log_message(__name__, f"{TEXT['info']} audit completed in {elapsed:.2f}s")

    # DUAL COPILOT validation
    valid = validate_results(len(results), analytics)
    if fail_on_findings and results:
        valid = False
    orchestrator = DualCopilotOrchestrator()
    orchestrator.validator.validate_corrections([r["file"] for r in results])
    if valid:
        log_message(__name__, f"{TEXT['success']} audit logged {len(results)} findings")
    else:
        log_message(
            __name__,
            f"{TEXT['error']} validation mismatch",
            level=logging.ERROR,
        )
    if export:
        export.write_text(json.dumps({"results": results, "valid": valid}))
    return valid


def parse_args(argv: Optional[List[str]] | None = None) -> argparse.Namespace:
    """Return CLI arguments for the audit script."""

    parser = argparse.ArgumentParser(
        description="Audit workspace for TODO/FIXME placeholders",
        epilog="For cleanup only, run scripts/placeholder_cleanup.py",
    )
    parser.add_argument("--workspace-path", type=str, help="Workspace to scan")
    parser.add_argument(
        "--analytics-db",
        type=str,
        default="databases/analytics.db",
        help="analytics.db location",
    )
    parser.add_argument("--production-db", type=str, help="production.db location")
    parser.add_argument("--dashboard-dir", type=str, help="dashboard/compliance directory")
    parser.add_argument("--dataset-path", type=str, help="Optional JSON dataset with additional patterns")
    parser.add_argument("--timeout-minutes", type=int, default=30, help="Scan timeout in minutes")
    parser.add_argument(
        "--simulate",
        action="store_true",
        dest="simulate",
        help="Run in test mode without writes",
    )
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
        dest="apply_fixes",
        help="Automatically remove placeholders and log corrections",
    )
    parser.add_argument(
        "--apply-suggestions",
        action="store_true",
        dest="apply_suggestions",
        help="Apply generated suggestions for simple placeholders",
    )
    parser.add_argument(
        "--auto-resolve",
        action="store_true",
        dest="auto_resolve",
        help="Automatically resolve placeholders and mark them resolved",
    )
    parser.add_argument(
        "--rollback-last",
        action="store_true",
        help="Rollback the most recent audit entry",
    )
    parser.add_argument("--rollback-id", type=int, help="Rollback a specific entry id")
    parser.add_argument("--export", type=Path, help="Export audit results to JSON")
    parser.add_argument(
        "--task-report",
        type=Path,
        help="Write unresolved placeholder tasks to JSON or Markdown",
    )
    parser.add_argument(
        "--summary-json",
        type=str,
        help="Explicit path for placeholder_summary.json output",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with failure if any placeholders are found",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.rollback_id is not None:
        target_id = args.rollback_id
        if rollback_last_entry(
            Path(args.analytics_db or Path.cwd() / "databases" / "analytics.db"),
            target_id,
        ):
            print(json.dumps({"rollback": True}))
            raise SystemExit(0)
        print(json.dumps({"rollback": False}))
        raise SystemExit(1)
    if args.rollback_last:
        result = rollback_last_entry(Path(args.analytics_db or Path.cwd() / "databases" / "analytics.db"))
        print(json.dumps({"rollback": result}))
        raise SystemExit(0 if result else 1)
    if args.test_mode:
        os.environ["GH_COPILOT_TEST_MODE"] = "1"
        args.simulate = True
    success = main(
        workspace_path=args.workspace_path,
        analytics_db=args.analytics_db,
        production_db=args.production_db,
        dashboard_dir=args.dashboard_dir,
        dataset_path=args.dataset_path,
        timeout_minutes=args.timeout_minutes,
        simulate=args.simulate,
        exclude_dirs=args.exclude_dirs,
        update_resolutions=args.update_resolutions,
        apply_fixes=args.apply_fixes,
        apply_suggestions=args.apply_suggestions,
        auto_resolve=args.auto_resolve,
        export=args.export,
        task_report=args.task_report,
        summary_json=args.summary_json,
        fail_on_findings=args.fail_on_findings,
    )
    raise SystemExit(0 if success else 1)
