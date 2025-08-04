#!/usr/bin/env python3
"""Lightweight orchestrator for Dual Copilot validation."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable, Iterable, Tuple

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator
from scripts.validation.primary_copilot_executor import PrimaryCopilotExecutor, ProcessPhase
from scripts.monitoring.unified_monitoring_optimization_system import (
    EnterpriseUtility,
    collect_metrics,
)
from utils.log_utils import _log_event


class DualCopilotOrchestrator:
    """Run a primary operation followed by secondary validation."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        monitor: EnterpriseUtility | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.validator = SecondaryCopilotValidator(self.logger)
        self.monitor = monitor or EnterpriseUtility()

    def run(
        self,
        primary: Callable[[], bool],
        validation_targets: Iterable[str],
        timeout_minutes: int = 30,
    ) -> Tuple[bool, bool, dict]:
        """Execute primary callable then validate targets, returning metrics."""
        start_time = datetime.utcnow()
        self.logger.info("[DUAL] Starting primary operation")

        executor = PrimaryCopilotExecutor("Primary Operation", timeout_minutes, self.logger)
        phase = ProcessPhase("Primary", "Execute main task", "\U0001f680", 100)
        _, primary_success = executor.execute_with_monitoring([phase], primary)

        if primary_success:
            self.logger.info("[DUAL] Primary operation succeeded")
        else:
            self.logger.error("[DUAL] Primary operation failed")

        validation_success = self.validator.validate_corrections(list(validation_targets))

        # Collect monitoring metrics regardless of validation outcome
        try:
            self.monitor.execute_utility()
        except Exception:  # pragma: no cover - best effort monitoring
            self.logger.exception("[DUAL] Monitoring execution failed")

        metrics = collect_metrics()
        end_time = datetime.utcnow()
        _log_event(
            {
                "event": "dual_copilot_run",
                "primary_success": primary_success,
                "validation_success": validation_success,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                **metrics,
            }
        )

        return primary_success, validation_success, metrics
