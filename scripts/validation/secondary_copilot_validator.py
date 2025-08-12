#!/usr/bin/env python3
"""SecondaryCopilotValidator - ensures corrected files pass flake8."""

from __future__ import annotations

import logging
import subprocess
import time
from typing import Any, Dict, List


class SecondaryCopilotValidator:
    """Run flake8 on a set of files and return validation result."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.metrics: Dict[str, Any] = {}

    def validate_corrections(
        self, files: List[str], primary_success: bool | None = None
    ) -> bool:
        """Return True if all files pass flake8 and record detailed metrics."""
        self.metrics = {
            "files_checked": list(files),
            "failed_files": [],
            "primary_success": primary_success,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "duration": 0.0,
        }
        if not files:
            return True
        cmd = ["flake8", *files]
        self.logger.info("Running secondary flake8 validation", extra=None)
        start = time.perf_counter()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            self.metrics["duration"] = time.perf_counter() - start
            self.metrics["returncode"] = -1
            self.metrics["stderr"] = "flake8 executable not found"
            self.logger.error("flake8 executable not found")
            return False
        self.metrics["duration"] = time.perf_counter() - start
        self.metrics["returncode"] = result.returncode
        self.metrics["stdout"] = result.stdout
        self.metrics["stderr"] = result.stderr
        if result.returncode == 0:
            self.logger.info("Secondary validation passed", extra=None)
            return True
        self.metrics["failed_files"] = list(files)
        if primary_success is False:
            self.logger.error(
                "Secondary validation after failing primary path failed:\n%s%s",
                result.stdout,
                result.stderr,
            )
        else:
            self.logger.error(
                "Secondary validation failed:\n%s%s",
                result.stdout,
                result.stderr,
            )
        return False
