#!/usr/bin/env python3
"""DatabaseDrivenFlake8CorrectorFunctional
========================================

Perform flake8 corrections on a workspace, tracking every fix in
``production.db``. Scanning handles non-ASCII paths and file content
in a Unicode-safe manner. After applying ``autopep8`` and ``isort``
corrections, the script triggers the secondary Copilot validator to
ensure compliance.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Dict, List

from tqdm import tqdm

from secondary_copilot_validator import SecondaryCopilotValidator

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
    "info": "[INFO]",
}


class DatabaseDrivenFlake8CorrectorFunctional:
    """Correct flake8 violations and record them in a database."""

    DEFAULT_TIMEOUT_MINUTES = 30

    def __init__(
        self,
        workspace_path: str | None = None,
        db_path: str = "production.db",
        timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES,
    ) -> None:
        env_default = Path.cwd()
        if os.name == "nt":
            self.workspace_path = Path(PureWindowsPath(workspace_path or env_default))
            self.db_path = Path(PureWindowsPath(db_path))
        else:
            self.workspace_path = Path(workspace_path or env_default)
            self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.validator = SecondaryCopilotValidator(self.logger)
        self.start_ts: float | None = None

    def scan_python_files(self) -> List[Path]:
        """Return a list of Python files under ``workspace_path``."""
        files = []
        for path in self.workspace_path.rglob("*.py"):
            if self._within_workspace(path):
                files.append(path)
        return files

    def _within_workspace(self, path: Path) -> bool:
        """Return True if ``path`` resides within ``workspace_path``."""
        try:
            path.resolve().relative_to(self.workspace_path)
            return True
        except ValueError:
            return False

    def _check_timeout(self) -> None:
        if self.start_ts and time.time() - self.start_ts > self.timeout_seconds:
            raise TimeoutError("Correction process exceeded timeout")

    def _init_progress(self, total_files: int) -> int:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS correction_progress ("
                "id INTEGER PRIMARY KEY CHECK (id=1),"
                "last_file_index INTEGER NOT NULL,"
                "total_files INTEGER NOT NULL,"
                "updated_at TEXT NOT NULL"
                ")"
            )
            row = conn.execute(
                "SELECT last_file_index, total_files FROM correction_progress "
                "WHERE id=1"
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE correction_progress SET total_files=?, updated_at=? WHERE id=1",
                    (total_files, now),
                )
                return int(row[0])
            conn.execute(
                "INSERT INTO correction_progress (id, last_file_index, total_files, updated_at) "
                "VALUES (1, 0, ?, ?)",
                (total_files, now),
            )
            return 0

    def _update_progress(self, index: int) -> None:
        if not self.db_path.exists():
            return
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE correction_progress SET last_file_index=?, updated_at=? WHERE id=1",
                (index, now),
            )

    def _compute_etc(self, processed: int, total: int) -> str:
        if processed == 0:
            return "unknown"
        elapsed = time.time() - (self.start_ts or time.time())
        remaining = (elapsed / processed) * (total - processed)
        etc_time = datetime.utcnow() + timedelta(seconds=remaining)
        return etc_time.isoformat()

    def run_flake8_scan(self, files: List[Path]) -> Dict[Path, List[str]]:
        """Run flake8 on each file and collect violation lines."""
        violations: Dict[Path, List[str]] = {}
        for file_path in files:
            cmd = ["flake8", str(file_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                violations[file_path] = result.stdout.strip().splitlines()
        return violations

    def apply_corrections(self, files: List[Path]) -> List[Path]:
        """Apply autopep8 and isort to each file and return corrected ones."""
        corrected: List[Path] = []
        for idx, path in enumerate(files, start=1):
            self._check_timeout()
            original = path.read_text(encoding="utf-8", errors="ignore")
            subprocess.run(["autopep8", "--in-place", str(path)], check=False)
            subprocess.run(["isort", str(path)], check=False)
            new_content = path.read_text(encoding="utf-8", errors="ignore")
            if original != new_content:
                corrected.append(path)
                self.validate_corrections([path])
            self._update_progress(idx)
            etc = self._compute_etc(idx, len(files))
            self.logger.info(
                f"{TEXT_INDICATORS['progress']} {idx}/{len(files)} ETC {etc}"
            )
        return corrected

    def record_corrections(self, violations: Dict[Path, List[str]], corrected: List[Path]) -> None:
        """Insert correction metadata into ``production.db``."""
        if not self.db_path.exists():
            return
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for file_path in corrected:
                for line in violations.get(file_path, []):
                    parts = line.split(":", 3)
                    if len(parts) < 4:
                        continue
                    _, row, _, rest = parts
                    code = rest.strip().split()[0]
                    cursor.execute(
                        "INSERT INTO correction_history (file_path, violation_code, original_line, corrected_line, correction_timestamp)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (
                            str(file_path),
                            code,
                            row,
                            row,
                            timestamp,
                        ),
                    )
            conn.commit()

    def validate_workspace(self) -> None:
        """Validate workspace for recursion and backup policy."""
        root_name = self.workspace_path.name.lower()
        for folder in self.workspace_path.rglob(root_name):
            if folder.is_dir() and folder != self.workspace_path:
                raise RuntimeError(f"Recursive folder detected: {folder}")

        backup_root_env = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if backup_root_env and "backup" in root_name:
            backup_root = (
                Path(PureWindowsPath(backup_root_env))
                if os.name == "nt"
                else Path(backup_root_env)
            )
            try:
                self.workspace_path.relative_to(backup_root)
            except ValueError as exc:
                raise RuntimeError(
                    f"Backups must be stored under {backup_root}"
                ) from exc

    def validate_corrections(self, files: List[Path]) -> bool:
        """Run secondary Copilot validation on ``files``."""
        return self.validator.validate_corrections([str(f) for f in files])

    def execute_correction(self) -> bool:
        """Run scan, apply fixes, record to DB, and validate."""
        start_dt = datetime.utcnow()
        self.start_ts = time.time()
        pid = os.getpid()
        self.logger.info(
            f"{TEXT_INDICATORS['start']} Correction started: {start_dt} PID {pid}"
        )
        try:
            self.validate_workspace()
            py_files = self.scan_python_files()
            start_idx = self._init_progress(len(py_files))
            with tqdm(total=len(py_files), desc=f"{TEXT_INDICATORS['progress']} scan", unit="file") as scan_bar:
                violations: Dict[Path, List[str]] = {}
                for idx, f in enumerate(py_files[start_idx:], start=start_idx + 1):
                    self._check_timeout()
                    file_violations = self.run_flake8_scan([f])
                    violations.update(file_violations)
                    scan_bar.update(1)
                    self._update_progress(idx)
            files_with_issues = list(violations.keys())
            with tqdm(total=len(files_with_issues), desc=f"{TEXT_INDICATORS['progress']} fix", unit="file") as fix_bar:
                corrected = self.apply_corrections(files_with_issues)
                fix_bar.update(len(files_with_issues))
            self.record_corrections(violations, corrected)
            valid = self.validate_corrections(corrected)
            duration = (datetime.utcnow() - start_dt).total_seconds()
            if valid:
                self.logger.info(
                    f"{TEXT_INDICATORS['success']} Correction completed in {duration:.1f}s"
                )
            else:
                self.logger.error(f"{TEXT_INDICATORS['error']} Validation failed")
            return valid
        except Exception as exc:  # pragma: no cover - unexpected error path
            self.logger.error(f"{TEXT_INDICATORS['error']} {exc}")
            return False


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    corrector = DatabaseDrivenFlake8CorrectorFunctional()
    success = corrector.execute_correction()
    raise SystemExit(0 if success else 1)
