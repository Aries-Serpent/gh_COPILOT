#!/usr/bin/env python3
"""DatabaseDrivenRuffCorrector
===============================

Apply ``ruff`` based corrections across a workspace and track each fix in
``production.db``. Corrections run ``ruff --fix`` followed by ``isort`` and
``autopep8``. The results are recorded in the existing ``correction_history``
table and validated using the ``cross_validate_with_ruff`` helper from
``enterprise_template_compliance_enhancer.py``.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path, PureWindowsPath
from typing import Dict, List

from tqdm import tqdm

from copilot.common.workspace_utils import _within_workspace
from secondary_copilot_validator import SecondaryCopilotValidator
from scripts.optimization.enterprise_template_compliance_enhancer import (
    EnterpriseFlake8Corrector,
)


TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
    "info": "[INFO]",
}


class DatabaseDrivenRuffCorrector:
    """Correct ruff violations and record them in a database."""

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
        self.cross_validator = EnterpriseFlake8Corrector(workspace_path=str(self.workspace_path))
        self.start_ts: float | None = None
        self.timeout_seconds = timeout_minutes * 60

    # ------------------------------------------------------------------ utils
    def scan_python_files(self) -> List[Path]:
        """Return a list of Python files under ``workspace_path``."""
        files: List[Path] = []
        for path in self.workspace_path.rglob("*.py"):
            if _within_workspace(path, self.workspace_path):
                files.append(path)
        return files

    def _check_timeout(self) -> None:
        if self.start_ts and time.time() - self.start_ts > self.timeout_seconds:
            raise TimeoutError("Correction process exceeded timeout")

    def _compute_etc(self, processed: int, total: int) -> str:
        if processed == 0:
            return "unknown"
        elapsed = time.time() - (self.start_ts or time.time())
        remaining = (elapsed / processed) * (total - processed)
        etc_time = datetime.utcnow() + timedelta(seconds=remaining)
        return etc_time.isoformat()

    # ----------------------------------------------------------- ruff routines
    def run_ruff_scan(self, files: List[Path]) -> Dict[Path, List[str]]:
        """Run ``ruff check`` on ``files`` and collect violation lines."""
        violations: Dict[Path, List[str]] = {}
        for file_path in files:
            result = subprocess.run(
                ["ruff", "check", str(file_path)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                violations[file_path] = result.stdout.strip().splitlines()
        return violations

    def apply_corrections(self, files: List[Path]) -> List[Path]:
        """Apply ``ruff --fix``, ``isort`` and ``autopep8`` to each file."""
        corrected: List[Path] = []
        for idx, path in enumerate(files, start=1):
            self._check_timeout()
            original = path.read_text(encoding="utf-8", errors="ignore")

            subprocess.run(["ruff", "check", "--fix", str(path)], check=False)
            subprocess.run(["isort", str(path)], check=False)
            subprocess.run(["autopep8", "--in-place", str(path)], check=False)

            new_content = path.read_text(encoding="utf-8", errors="ignore")
            if original != new_content:
                corrected.append(path)
                # secondary validation and ruff cross-check
                self.validator.validate_corrections([str(path)])
                self.cross_validator.cross_validate_with_ruff(path, str(path))

            etc = self._compute_etc(idx, len(files))
            self.logger.info(f"{TEXT_INDICATORS['progress']} {idx}/{len(files)} ETC {etc}")
        return corrected

    def record_corrections(self, violations: Dict[Path, List[str]], corrected: List[Path]) -> None:
        """Insert correction metadata into ``production.db``."""
        if not self.db_path.exists():
            return
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for file_path in corrected:
                corrected_lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in violations.get(file_path, []):
                    parts = line.split(":", 3)
                    if len(parts) < 4:
                        continue
                    _, row, _, rest = parts
                    code = rest.strip().split()[0]
                    row_num = int(row)
                    corrected_line = corrected_lines[row_num - 1] if row_num <= len(corrected_lines) else ""
                    cursor.execute(
                        "INSERT INTO correction_history (file_path, "
                        "violation_code, original_line, corrected_line, correction_timestamp)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (
                            str(file_path),
                            code,
                            row,
                            corrected_line,
                            timestamp,
                        ),
                    )
            conn.commit()

    # ------------------------------------------------------------- main entry
    def execute_correction(self) -> bool:
        """Run scan, apply fixes, record to DB, and validate."""
        start_dt = datetime.utcnow()
        self.start_ts = time.time()
        pid = os.getpid()
        self.logger.info(f"{TEXT_INDICATORS['start']} Correction started: {start_dt} PID {pid}")
        try:
            py_files = self.scan_python_files()
            with tqdm(total=len(py_files), desc=f"{TEXT_INDICATORS['progress']} scan", unit="file") as scan_bar:
                violations = self.run_ruff_scan(py_files)
                for _ in py_files:
                    scan_bar.update(1)
            with tqdm(total=len(py_files), desc=f"{TEXT_INDICATORS['progress']} fix", unit="file") as fix_bar:
                corrected = self.apply_corrections(list(violations.keys()))
                for _ in corrected:
                    fix_bar.update(1)
            self.record_corrections(violations, corrected)
            duration = (datetime.utcnow() - start_dt).total_seconds()
            self.logger.info(f"{TEXT_INDICATORS['success']} Correction completed in {duration:.1f}s")
            return True
        except Exception as exc:  # pragma: no cover - unexpected error path
            self.logger.error(f"{TEXT_INDICATORS['error']} {exc}")
            return False


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    corrector = DatabaseDrivenRuffCorrector()
    success = corrector.execute_correction()
    raise SystemExit(0 if success else 1)
