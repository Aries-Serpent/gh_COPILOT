<<<<<<< HEAD
"""Compatibility wrapper exposing secondary validation utilities."""

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator
from utils.validation_utils import run_dual_copilot_validation


def run_flake8(files: list[str]) -> bool:
    """Run secondary flake8 validation on ``files``.

    This convenience wrapper aligns with the dual-copilot pattern by
    delegating to :class:`SecondaryCopilotValidator` after code generation
    or modification steps.
    """

    validator = SecondaryCopilotValidator()
    return validator.validate_corrections(files)


__all__ = [
    "SecondaryCopilotValidator",
    "run_dual_copilot_validation",
    "run_flake8",
]
=======
#!/usr/bin/env python3
"""SecondaryCopilotValidator - ensures corrected files pass flake8."""

from __future__ import annotations

import logging
import subprocess
from typing import List


class SecondaryCopilotValidator:
    """Run flake8 on a set of files and return validation result."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def validate_corrections(self, files: List[str]) -> bool:
        """Return True if all files pass flake8."""
        if not files:
            return True
        cmd = ["flake8", *files]
        self.logger.info("Running secondary flake8 validation", extra=None)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info("Secondary validation passed", extra=None)
            return True
        self.logger.error(
            "Secondary validation failed:\n%s%s",
            result.stdout,
            result.stderr,
        )
        return False
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
