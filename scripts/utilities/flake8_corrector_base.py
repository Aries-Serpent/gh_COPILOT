#!/usr/bin/env python3
"""Shared Flake8 correction utilities."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from utils.log_utils import _log_event

from tqdm import tqdm


class EnterpriseFlake8Corrector:
    """Common functionality for simple flake8 based corrections."""

    def __init__(self, workspace_path: str = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")) -> None:
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger(__name__)
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"

    def execute_correction(self) -> bool:
        """Execute correction over all python files."""
        start_time = datetime.now()
        self.logger.info("[START] Correction started: %s", start_time)
        try:
            with tqdm(total=100, desc="[PROGRESS] Flake8 Correction", unit="%") as pbar:
                pbar.set_description("[PROGRESS] Scanning files")
                files = self.scan_python_files()
                pbar.update(25)

                pbar.set_description("[PROGRESS] Applying corrections")
                corrected = self.apply_corrections(files)
                pbar.update(50)

                pbar.set_description("[PROGRESS] Validating results")
                valid = self.validate_corrections(corrected)
                pbar.update(25)

            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info("[SUCCESS] Correction completed in %.1fs", duration)
            return valid
        except Exception as e:
            self.logger.error("[ERROR] Correction failed: %s", e)
            return False

    def scan_python_files(self) -> list[str]:
        """Return a list of python files under the workspace."""
        return [str(p) for p in self.workspace_path.rglob("*.py")]

    def apply_corrections(self, files: list[str]) -> list[str]:
        """Apply corrections to provided files."""
        corrected = []
        for file_path in files:
            if self.correct_file(file_path):
                corrected.append(file_path)
                self.log_correction(file_path)
        return corrected

    def log_correction(self, file_path: str, event: str = "flake8_correction") -> None:
        """Record a correction action in analytics.db."""
        _log_event(
            {
                "event": event,
                "path": file_path,
            },
            table="correction_logs",
            db_path=self.analytics_db,
        )

    def correct_file(self, file_path: str) -> bool:  # pragma: no cover - overridden
        """Correct a single file using basic formatting tools.

        Subclasses **should** override this method to implement specialized
        correction behaviour. The default implementation simply runs ``isort``
        and ``autopep8`` over the provided file. It returns ``True`` if the file
        contents changed.
        """

        try:
            original = Path(file_path).read_text(encoding="utf-8")

            subprocess.run(
                [sys.executable, "-m", "isort", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            subprocess.run(
                [sys.executable, "-m", "autopep8", "--in-place", file_path],
                capture_output=True,
                text=True,
                check=False,
            )

            updated = Path(file_path).read_text(encoding="utf-8")
            return original != updated
        except Exception as exc:  # pragma: no cover - rare failure
            self.logger.error("[ERROR] File correction failed: %s", exc)
            return False

    def validate_corrections(self, files: list[str]) -> bool:
        """Basic validation that something changed."""
        return bool(files)

    def cross_validate_with_ruff(self, path: Path, original: str) -> bool:
        """Run ``ruff`` on *path* to ensure no new violations were introduced."""
        result = subprocess.run(["ruff", "check", str(path)], capture_output=True, text=True)
        return result.returncode == 0


class WhitespaceCorrector(EnterpriseFlake8Corrector):
    """Correct common whitespace issues (E1xx/E2xx)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            original = Path(file_path).read_text(encoding="utf-8")
            subprocess.run(
                [sys.executable, "-m", "autopep8", "--aggressive", "--in-place", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            updated = Path(file_path).read_text(encoding="utf-8")
            changed = original != updated
            if changed:
                self.logger.info("Fixed whitespace in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Whitespace correction failed: %s", exc)
            return False


class ImportOrderCorrector(EnterpriseFlake8Corrector):
    """Correct import order and remove unused imports (F401/F403)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            original = Path(file_path).read_text(encoding="utf-8")
            subprocess.run(
                [sys.executable, "-m", "isort", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            subprocess.run(
                [sys.executable, "-m", "autopep8", "--in-place", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            updated = Path(file_path).read_text(encoding="utf-8")
            changed = original != updated
            if changed:
                self.logger.info("Fixed imports in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Import correction failed: %s", exc)
            return False


class LineLengthCorrector(EnterpriseFlake8Corrector):
    """Fix E501 line length violations."""

    def correct_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            updated_lines = []
            changed = False
            for line in lines:
                stripped = line.rstrip("\n")
                if len(stripped) > 79:
                    updated_lines.append(stripped[:79] + "\n" + stripped[79:] + "\n")
                    changed = True
                else:
                    updated_lines.append(line)
            if changed:
                path.write_text("".join(updated_lines), encoding="utf-8")
                self.logger.info("Fixed line length in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Line length correction failed: %s", exc)
            return False


class TrailingWhitespaceCorrector(EnterpriseFlake8Corrector):
    """Remove trailing whitespace from lines (W293)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            updated_lines = []
            changed = False
            for line in lines:
                stripped_newline = line.rstrip("\n")
                cleaned = stripped_newline.rstrip(" \t")
                if cleaned != stripped_newline:
                    updated_lines.append(cleaned + "\n")
                    changed = True
                else:
                    updated_lines.append(line)
            if changed:
                path.write_text("".join(updated_lines), encoding="utf-8")
                self.logger.info("Removed trailing whitespace in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Trailing whitespace correction failed: %s", exc)
            return False


class IndentationCorrector(EnterpriseFlake8Corrector):
    """Correct indentation issues (E11x/E12x)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            updated_lines = []
            changed = False
            for i, line in enumerate(lines):
                if i > 0 and line.strip() and not line.startswith(" "):
                    updated_lines.append("    " + line)
                    changed = True
                else:
                    updated_lines.append(line)
            if changed:
                path.write_text("".join(updated_lines), encoding="utf-8")
                self.logger.info("Fixed indentation in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Indentation correction failed: %s", exc)
            return False


class ComplexityCorrector(EnterpriseFlake8Corrector):
    """Mark files that exceed complexity limits (C901)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    "--select",
                    "C90",
                    "--max-complexity",
                    "10",
                    file_path,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if not result.stdout:
                return False

            original = Path(file_path).read_text(encoding="utf-8")
            Path(file_path).write_text(
                "# TODO: reduce complexity\n" + original,
                encoding="utf-8",
            )
            self.logger.info("Marked complexity in %s", file_path)
            return True
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Complexity correction failed: %s", exc)
            return False


class UndefinedNameCorrector(EnterpriseFlake8Corrector):
    """Mark files containing undefined names (F821)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    "--select",
                    "F821",
                    file_path,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if not result.stdout:
                return False

            original = Path(file_path).read_text(encoding="utf-8")
            Path(file_path).write_text(
                "# TODO: fix undefined names\n" + original,
                encoding="utf-8",
            )
            self.logger.info("Marked undefined names in %s", file_path)
            return True
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Undefined name correction failed: %s", exc)
            return False


class BlankLinesCorrector(EnterpriseFlake8Corrector):
    """Ensure two blank lines before top-level definitions (E302)."""

    def correct_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            changed = False
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.lstrip()
                if stripped.startswith("def ") or stripped.startswith("class "):
                    blank_count = 0
                    j = i - 1
                    while j >= 0 and lines[j].strip() == "":
                        blank_count += 1
                        j -= 1
                    needed = 2 - blank_count
                    if needed > 0:
                        for _ in range(needed):
                            lines.insert(i, "\n")
                            i += 1
                        changed = True
                i += 1
            if changed:
                path.write_text("".join(lines), encoding="utf-8")
                self.logger.info("Added blank lines in %s", file_path)
            return changed
        except Exception as exc:  # pragma: no cover - unexpected
            self.logger.error("Blank line correction failed: %s", exc)
            return False


__all__ = [
    "EnterpriseFlake8Corrector",
    "WhitespaceCorrector",
    "ImportOrderCorrector",
    "LineLengthCorrector",
    "TrailingWhitespaceCorrector",
    "IndentationCorrector",
    "ComplexityCorrector",
    "UndefinedNameCorrector",
    "BlankLinesCorrector",
]
