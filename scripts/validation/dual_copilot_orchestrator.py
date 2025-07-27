#!/usr/bin/env python3
"""Lightweight orchestrator for Dual Copilot validation."""
from __future__ import annotations

import logging
from typing import Callable, Iterable

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator


class DualCopilotOrchestrator:
    """Run a primary operation followed by secondary validation."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.validator = SecondaryCopilotValidator(self.logger)

    def run(self, primary: Callable[[], bool], validation_targets: Iterable[str]) -> bool:
        """Execute primary callable then validate the given targets."""
        self.logger.info("[DUAL] Starting primary operation")
        primary_success = primary()
        if primary_success:
            self.logger.info("[DUAL] Primary operation succeeded")
        else:
            self.logger.error("[DUAL] Primary operation failed")
        validation_success = self.validator.validate_corrections(list(validation_targets))
        return primary_success and validation_success
