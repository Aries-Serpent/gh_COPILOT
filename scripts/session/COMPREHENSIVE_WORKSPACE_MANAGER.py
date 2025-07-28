#!/usr/bin/env python3
"""Comprehensive Workspace Manager.

This module implements start and end session management following
COMPREHENSIVE_SESSION_INTEGRITY instructions. It performs workspace
integrity validation, zero-byte file detection, anti-recursion checks and
logs the session lifecycle into ``production.db``. Execution is wrapped by
the DUAL COPILOT pattern for additional validation.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

from scripts.monitoring.unified_monitoring_optimization_system import (
    EnterpriseUtility,
)
from scripts.utilities.emergency_c_temp_violation_prevention import (
    EmergencyAntiRecursionValidator,
)

from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator


DB_PATH = Path("databases/production.db")


def get_connection(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


class ComprehensiveWorkspaceManager:
    """Manage session lifecycle with integrity checks."""

    def __init__(self, *, db_path: Path = DB_PATH, autofix: bool = False, verbose: bool = False) -> None:
        self.db_path = db_path
        self.autofix = autofix
        self.verbose = verbose
        self.workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
        self.logger = logging.getLogger(self.__class__.__name__)
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp"))
        backup_root.mkdir(parents=True, exist_ok=True)
        # runtime path for session ID file ensures one session at a time
        self.session_file = backup_root / "current_session_id.txt"

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------
    def _setup_logging(self) -> None:
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    def _validate_environment(self) -> None:
        backup_root = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if not backup_root:
            raise EnvironmentError("GH_COPILOT_BACKUP_ROOT is not set")
        Path(backup_root).mkdir(parents=True, exist_ok=True)

    def _scan_zero_byte_files(self) -> List[Path]:
        files: List[Path] = []
        for path in self.workspace.rglob("*"):
            if path.is_file() and path.stat().st_size == 0:
                files.append(path)
        return files

    def _scan_recursive_folders(self) -> List[Path]:
        folders: List[Path] = []
        for path in self.workspace.rglob("*"):
            if path.is_dir() and "backup" in path.name.lower() and path != self.workspace:
                folders.append(path)
        return folders

    def _remove_paths(self, paths: Iterable[Path]) -> None:
        """Remove zero-byte files or recursive folders."""
        for p in paths:
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------
    def _insert_session(self) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO session_wrapups (
                    process_id, start_time, status, errors_count, warnings_count, completed_tasks, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"CWM-{os.getpid()}-{int(time.time())}",
                    datetime.now(UTC).isoformat(),
                    "RUNNING",
                    0,
                    0,
                    "",
                    "session start",
                ),
            )
            conn.commit()
            row_id = cur.lastrowid
            assert row_id is not None
            return row_id

    def _finalize_session(self, row_id: int) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE session_wrapups
                   SET end_time = ?, status = ?
                 WHERE id = ?
                """,
                (datetime.now(UTC).isoformat(), "COMPLETED", row_id),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_workspace(self) -> None:
        zero_files = self._scan_zero_byte_files()
        recursive_folders = self._scan_recursive_folders()

        if zero_files:
            self.logger.warning("Zero-byte files found: %s", zero_files)
            if self.autofix:
                self._remove_paths(zero_files)

        if recursive_folders:
            self.logger.error("Recursive backup folders found: %s", recursive_folders)
            if self.autofix:
                self._remove_paths(recursive_folders)

    # ------------------------------------------------------------------
    # Session operations
    # ------------------------------------------------------------------
    def start_session(self) -> bool:
        """Start a managed session."""
        self._setup_logging()
        self._validate_environment()
        phases = ["PreValidation", "Scanning", "Logging", "PostValidation"]
        start_time = time.time()
        with tqdm(total=len(phases), desc="SessionStart", unit="step") as bar:
            for phase in phases:
                if time.time() - start_time > 1800:  # 30 minutes
                    raise TimeoutError("Session start exceeded timeout")
                remaining = len(phases) - bar.n
                etc = start_time + remaining * 2
                bar.set_description(f"{phase} ETA:{time.strftime('%H:%M:%S', time.localtime(etc))}")
                if phase == "PreValidation":
                    EmergencyAntiRecursionValidator().emergency_cleanup()
                    EnterpriseUtility().execute_utility()
                elif phase == "Scanning":
                    self._validate_workspace()
                elif phase == "Logging":
                    row_id = self._insert_session()
                    self.session_file.write_text(str(row_id))
                elif phase == "PostValidation":
                    self._validate_workspace()
                bar.update(1)
        return True

    def end_session(self) -> bool:
        """Finalize the managed session."""
        self._setup_logging()
        self._validate_environment()
        if not self.session_file.exists():
            raise RuntimeError("No active session to finalize")
        row_id = int(self.session_file.read_text())

        phases = ["Scanning", "Finalize", "PostValidation", "FinalScan"]
        start_time = time.time()
        with tqdm(total=len(phases), desc="SessionEnd", unit="step") as bar:
            for phase in phases:
                if time.time() - start_time > 1800:
                    raise TimeoutError("Session end exceeded timeout")
                remaining = len(phases) - bar.n
                etc = start_time + remaining * 2
                bar.set_description(f"{phase} ETA:{time.strftime('%H:%M:%S', time.localtime(etc))}")
                if phase == "Scanning":
                    self._validate_workspace()
                elif phase == "Finalize":
                    self._finalize_session(row_id)
                    self.session_file.unlink(missing_ok=True)
                elif phase == "PostValidation":
                    EmergencyAntiRecursionValidator().full_validation()
                    EnterpriseUtility().execute_utility()
                elif phase == "FinalScan":
                    self._validate_workspace()
                bar.update(1)
        return True


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Comprehensive Workspace Manager")
    parser.add_argument("--SessionStart", action="store_true", help="Start session")
    parser.add_argument("--SessionEnd", action="store_true", help="End session")
    parser.add_argument("-AutoFix", action="store_true", help="Automatically fix issues")
    parser.add_argument("-VerboseLogging", action="store_true", help="Enable verbose logging")
    parser.add_argument("--db-path", type=Path, default=DB_PATH, help="Path to production database")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    manager = ComprehensiveWorkspaceManager(db_path=args.db_path, autofix=args.AutoFix, verbose=args.VerboseLogging)

    orchestrator = DualCopilotOrchestrator()

    if args.SessionStart == args.SessionEnd:
        raise SystemExit("Specify --SessionStart or --SessionEnd")

    if args.SessionStart:
        orchestrator.run(manager.start_session, [__file__])
    else:
        orchestrator.run(manager.end_session, [__file__])


if __name__ == "__main__":  # pragma: no cover
    main()
