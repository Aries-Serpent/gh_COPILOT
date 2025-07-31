#!/usr/bin/env python3
"""PrimaryCopilotExecutor with visual indicators and timeout control."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Tuple

from tqdm import tqdm

LOGGER = logging.getLogger(__name__)


@dataclass
class ProcessPhase:
    """Definition of a processing phase used for progress reporting."""

    name: str
    description: str
    icon: str
    weight: int


@dataclass
class ExecutionResult:
    """Summary of the execution run."""

    task_name: str
    start_time: datetime
    completion_time: datetime
    process_id: int
    has_progress_indicators: bool
    has_timeout_controls: bool
    has_start_time_logging: bool
    has_etc_calculation: bool
    phases_completed: int


class PrimaryCopilotExecutor:
    """Execute tasks with mandatory visual indicators and timeout handling."""

    def __init__(self, task_name: str, timeout_minutes: int = 30, logger: logging.Logger | None = None) -> None:
        self.task_name = task_name
        self.start_time = datetime.now()
        self.timeout_seconds = timeout_minutes * 60
        self.process_id = os.getpid()
        self.logger = logger or LOGGER

        self.setup_visual_monitoring()
        if os.getenv("GH_COPILOT_DISABLE_VALIDATION") != "1":
            self.validate_environment_compliance()

    # ------------------------------------------------------------------
    def validate_environment_compliance(self) -> None:
        """Validate workspace path and check for forbidden recursive folders."""
        workspace_root = Path(os.getcwd())
        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations: List[str] = []
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))
        if violations:
            self.logger.error("\ud83d\udea8 RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                self.logger.error("   - %s", violation)
            raise RuntimeError("CRITICAL: Recursive folder violations prevent execution")
        if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
            self.logger.warning("\u26a0\ufe0f Non-standard workspace root: %s", workspace_root)
        self.logger.info("\u2705 ENVIRONMENT COMPLIANCE VALIDATED")

    def setup_visual_monitoring(self) -> None:
        """Log initialization details for visual monitoring."""
        self.logger.info("=" * 60)
        self.logger.info("\ud83d\ude80 PRIMARY COPILOT EXECUTOR INITIALIZED")
        self.logger.info("Task: %s", self.task_name)
        self.logger.info("Start Time: %s", self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.logger.info("Process ID: %s", self.process_id)
        self.logger.info("Timeout: %.1f minutes", self.timeout_seconds / 60)
        self.logger.info("=" * 60)

    # ------------------------------------------------------------------
    def _check_timeout(self) -> None:
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > self.timeout_seconds:
            raise TimeoutError(f"Process exceeded {self.timeout_seconds / 60:.1f} minute timeout")

    def _calculate_etc(self, elapsed: float, progress: float) -> float:
        if progress > 0:
            total_estimated = elapsed / (progress / 100)
            return max(0, total_estimated - elapsed)
        return 0.0

    def _log_completion_summary(self) -> None:
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info("=" * 60)
        self.logger.info("\u2705 PRIMARY COPILOT EXECUTION COMPLETE")
        self.logger.info("Task: %s", self.task_name)
        self.logger.info("Total Duration: %.1f seconds", duration)
        self.logger.info("Process ID: %s", self.process_id)
        self.logger.info("Completion Status: SUCCESS")
        self.logger.info("=" * 60)

    # ------------------------------------------------------------------
    def execute_with_monitoring(
        self,
        phases: List[ProcessPhase],
        operation: Callable[[], bool] | None = None,
    ) -> Tuple[ExecutionResult, bool]:
        """Execute phases while reporting progress."""
        total_steps = sum(p.weight for p in phases)
        current_step = 0
        success = True
        with tqdm(
            total=100,
            desc=self.task_name,
            unit="%",
            bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]",
        ) as pbar:
            for idx, phase in enumerate(phases):
                self._check_timeout()
                pbar.set_description(f"{phase.icon} {phase.name}")
                self.logger.info("\ud83d\udcca %s: %s", phase.name, phase.description)
                if idx == 0 and operation is not None:
                    try:
                        success = bool(operation())
                    except Exception as exc:  # pragma: no cover - logging side
                        self.logger.error("Phase '%s' failed: %s", phase.name, exc)
                        success = False
                current_step += phase.weight
                progress = (current_step / total_steps) * 100
                pbar.update(phase.weight * 100 / total_steps)
                elapsed = (datetime.now() - self.start_time).total_seconds()
                etc = self._calculate_etc(elapsed, progress)
                self.logger.info(
                    "\u23f1\ufe0f Progress: %.1f%% | Elapsed: %.1fs | ETC: %.1fs",
                    progress,
                    elapsed,
                    etc,
                )
        self._log_completion_summary()
        result = ExecutionResult(
            task_name=self.task_name,
            start_time=self.start_time,
            completion_time=datetime.now(),
            process_id=self.process_id,
            has_progress_indicators=True,
            has_timeout_controls=True,
            has_start_time_logging=True,
            has_etc_calculation=True,
            phases_completed=len(phases),
        )
        return result, success
