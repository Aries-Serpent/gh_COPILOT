# [Script]: WLC Session Manager
# > Generated: 2025-07-24 06:45 | Author: mbaetiong

"""WLC Session Manager

Implements the Wrapping, Logging, and Compliance (WLC) methodology.
 - Wraps session operations with environment validation
 - Logs progress to the production database
 - Records compliance scores for auditing

Enterprise features:
 - Database-driven configuration
 - Progress indicators via tqdm
 - Designed for continuous operation and dual validation

When run as a standalone script, the repository root is automatically added to
``sys.path`` so project modules resolve correctly. Ensure the
``GH_COPILOT_WORKSPACE`` and ``GH_COPILOT_BACKUP_ROOT`` environment variables are
set before execution.
"""

from __future__ import annotations

# pyright: reportMissingModuleSource=false
import argparse
import logging
import os
import sqlite3
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from tqdm import tqdm

try:
    from gh_copilot.validation.secondary_copilot_validator import SecondaryCopilotValidator
except Exception:
    from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator  # type: ignore
from utils.cross_platform_paths import CrossPlatformPathManager
from utils.validation_utils import anti_recursion_guard, validate_enterprise_environment
from utils.lessons_learned_integrator import (
    extract_lessons_from_codex_logs,
    store_lesson,
)
from unified_session_management_system import ensure_no_zero_byte_files
from utils.logging_utils import ANALYTICS_DB
from utils.codex_log_db import (
    init_codex_log_db,
    record_codex_action,
    log_codex_end,
    finalize_codex_log_db,
)
from utils.codex_logger import init_db as init_codex_logs_db, log_action as log_codex_logger_action


def log_action(session_id: str, action: str, statement: str) -> None:
    """Log a codex action with a UTC timestamp."""
    record_codex_action(session_id, action, statement, datetime.now(UTC).isoformat())
    log_codex_logger_action(action, statement)

try:
    from scripts.orchestrators.unified_wrapup_orchestrator import (
        UnifiedWrapUpOrchestrator,
    )
except Exception:  # pragma: no cover - allow lazy import
    UnifiedWrapUpOrchestrator = None

DEFAULT_DB = CrossPlatformPathManager.get_workspace_path() / "databases" / "production.db"
DB_PATH = Path(os.getenv("WLC_DB_PATH", str(DEFAULT_DB)))


def get_connection(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def ensure_session_table(conn: sqlite3.Connection) -> None:
    """Create unified_wrapup_sessions table if it does not exist."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS unified_wrapup_sessions (
            session_id TEXT,
            start_time TEXT,
            status TEXT,
            end_time TEXT,
            compliance_score REAL,
            error_details TEXT,
            zero_byte_files INTEGER DEFAULT 0
        )
        """
    )
    cur.execute("PRAGMA table_info(unified_wrapup_sessions)")
    cols = [row[1] for row in cur.fetchall()]
    if "zero_byte_files" not in cols:
        cur.execute(
            "ALTER TABLE unified_wrapup_sessions ADD COLUMN zero_byte_files INTEGER DEFAULT 0"
        )
    conn.commit()


def initialize_database(db_path: Path) -> None:
    """Pre-run check to ensure required tables exist."""
    if os.getenv("TEST_MODE"):
        return
    with get_connection(db_path) as conn:
        ensure_session_table(conn)


def setup_logging(verbose: bool) -> Path:
    """Configure enterprise logging to external backup root."""
    backup_root = CrossPlatformPathManager.get_backup_root()
    log_dir = backup_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"wlc_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    return log_file


def start_session_entry(conn: sqlite3.Connection) -> tuple[int | None, str]:
    cur = conn.cursor()
    start_time = datetime.now(UTC).isoformat()
    session_id = f"WLC-{start_time}"
    cur.execute(
        """
        INSERT INTO unified_wrapup_sessions (
            session_id, start_time, status
        ) VALUES (?, ?, ?)
        """,
        (session_id, start_time, "RUNNING"),
    )
    conn.commit()
    return cur.lastrowid, session_id


def finalize_session_entry(
    conn: sqlite3.Connection,
    entry_id: int,
    compliance_score: float,
    *,
    zero_byte_files: int = 0,
    error: str | None = None,
) -> None:
    cur = conn.cursor()
    end_time = datetime.now(UTC).isoformat()
    cur.execute(
        """
        UPDATE unified_wrapup_sessions
        SET end_time = ?, status = ?, compliance_score = ?, error_details = ?, zero_byte_files = ?
        WHERE rowid = ?
        """,
        (
            end_time,
            "COMPLETED" if not error else "FAILED",
            compliance_score,
            error,
            zero_byte_files,
            entry_id,
        ),
    )
    conn.commit()


def _zero_byte_count(session_id: str) -> int:
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM zero_byte_files WHERE session_id=?",
                (session_id,),
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0
    except Exception:  # pragma: no cover - logging only
        logging.exception("Failed to read zero-byte scan results")
        return 0


def validate_environment() -> bool:
    """Validate enterprise workspace and backup paths."""
    try:
        validate_enterprise_environment()
    except EnvironmentError as exc:
        raise EnvironmentError("Required environment variables are not set or paths invalid") from exc
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run WLC session manager")
    parser.add_argument(
        "--steps",
        type=int,
        default=3,
        help="Number of steps to execute during the session",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Path to production database",
    )
    parser.add_argument(
        "--orchestrate",
        action="store_true",
        help="Run UnifiedWrapUpOrchestrator after session completion",
    )
    parser.add_argument(
        "--wrap-up",
        action="store_true",
        help="Package session artifacts and commit codex log",
    )
    return parser.parse_args(argv)


def run_session(steps: int, db_path: Path, verbose: bool, *, run_orchestrator: bool = False) -> None:
    if os.getenv("TEST_MODE") == "1":
        logging.debug("TEST_MODE=1; skipping run_session")
        return  # Skip side effects during tests
    if not validate_environment():
        raise EnvironmentError("Required environment variables are not set or paths invalid")
    setup_logging(verbose)
    logging.info("WLC session starting")

    global UnifiedWrapUpOrchestrator
    if UnifiedWrapUpOrchestrator is None:
        from scripts.orchestrators.unified_wrapup_orchestrator import (
            UnifiedWrapUpOrchestrator as _Orchestrator,
        )

        UnifiedWrapUpOrchestrator = _Orchestrator

    with get_connection(db_path) as conn:
        ensure_session_table(conn)
        entry_id, session_id = start_session_entry(conn)
        if entry_id is None:
            raise RuntimeError("Failed to create session entry in the database.")
        init_codex_log_db()
        init_codex_logs_db()
        log_action(session_id, "session_start", "WLC session starting")
        record_codex_action(
            session_id,
            "start",
            "WLC session starting",
            datetime.now(UTC).isoformat(),
        )
        compliance_score = 1.0
        try:
            with ensure_no_zero_byte_files(
                CrossPlatformPathManager.get_workspace_path(), session_id
            ):
                for i in tqdm(range(steps), desc="WLC Session", unit="step"):
                    logging.info("Step %d/%d completed", i + 1, steps)
                    log_action(
                        session_id,
                        "step_complete",
                        f"Step {i + 1}/{steps} completed",
                    )
                    sleep_time = 0.1
                    if os.getenv("TEST"):
                        sleep_time = 0.01
                    time.sleep(sleep_time)
                record_codex_action(
                    session_id,
                    "generation",
                    f"Generated {steps} steps",
                    datetime.now(UTC).isoformat(),
                )
                orchestrator = UnifiedWrapUpOrchestrator(
                    workspace_path=str(CrossPlatformPathManager.get_workspace_path())
                )
                log_action(session_id, "orchestrator_start", "Executing orchestrator")
                result = orchestrator.execute_unified_wrapup()
                compliance_score = result.compliance_score / 100.0
                log_action(
                    session_id,
                    "orchestrator_complete",
                    f"Orchestrator finished with score {compliance_score:.2f}",
                )
        except Exception as exc:  # noqa: BLE001
            logging.exception("WLC session failed")
            log_action(session_id, "session_failure", str(exc))
            zero_count = _zero_byte_count(session_id)
            finalize_session_entry(
                conn, entry_id, 0.0, zero_byte_files=zero_count, error=str(exc)
            )
            raise

        zero_count = _zero_byte_count(session_id)
        finalize_session_entry(
            conn, entry_id, compliance_score, zero_byte_files=zero_count
        )
        log_action(
            session_id,
            "session_end",
            f"Session completed with score {compliance_score:.2f}",
        )
        store_lesson(
            description=f"WLC session completed with score {compliance_score:.2f}",
            source="wlc_session_manager",
            timestamp=datetime.now(UTC).isoformat(),
            validation_status="validated",
            tags="wlc",
        )
        codex_db = CrossPlatformPathManager.get_workspace_path() / "databases" / "codex_log.db"
        # Derive actionable lessons from Codex log patterns
        for lesson in extract_lessons_from_codex_logs(codex_db):
            store_lesson(**lesson)

        if run_orchestrator:
            orchestrator_cls = UnifiedWrapUpOrchestrator
            if orchestrator_cls is None:
                from scripts.orchestrators.unified_wrapup_orchestrator import (
                    UnifiedWrapUpOrchestrator as orchestrator_cls,
                )

            orchestrator = orchestrator_cls(
                workspace_path=str(CrossPlatformPathManager.get_workspace_path())
            )
            log_action(session_id, "post_session_orchestrator_start", "Running orchestrator post session")
            orchestrator.execute_unified_wrapup()
            log_action(session_id, "post_session_orchestrator_complete", "Post session orchestrator finished")

        validator = SecondaryCopilotValidator()
        validator.validate_corrections([__file__])
        record_codex_action(
            session_id,
            "validation",
            "Secondary copilot validation complete",
            datetime.now(UTC).isoformat(),
        )

    if os.getenv("WLC_RUN_ORCHESTRATOR") == "1":
        orchestrator = UnifiedWrapUpOrchestrator(
            workspace_path=str(CrossPlatformPathManager.get_workspace_path())
        )
        log_action(session_id, "env_orchestrator_start", "Running orchestrator via env flag")
        orchestrator.execute_unified_wrapup()
        log_action(session_id, "env_orchestrator_complete", "Env orchestrator finished")
    record_codex_action(
        session_id,
        "wrap_up",
        "WLC session wrap-up finalized",
        datetime.now(UTC).isoformat(),
    )
    log_codex_end(session_id, "WLC session wrap-up finalized")
    finalize_codex_log_db()
    logging.info("WLC session completed")


@anti_recursion_guard
def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if os.getenv("TEST_MODE") == "1" and not args.wrap_up:
        logging.debug("TEST_MODE=1; exiting early")
        return
    if args.wrap_up:
        from artifact_manager import LfsPolicy, package_session

        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        package_session(
            tmp_dir,
            repo_root,
            LfsPolicy(repo_root),
            commit=os.getenv("TEST_MODE") != "1",
            message="chore: add session wrap-up artifact",
        )
        return
    initialize_database(args.db_path)
    run_session(
        args.steps,
        args.db_path,
        args.verbose,
        run_orchestrator=args.orchestrate,
    )


if __name__ == "__main__":
    main()
