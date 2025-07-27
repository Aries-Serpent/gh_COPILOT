#!/usr/bin/env python3
"""Lightweight orchestrator implementing the dual copilot pattern."""

from __future__ import annotations

import logging
from typing import Any, Callable, Iterable

from .secondary_copilot_validator import SecondaryCopilotValidator


class DualCopilotOrchestrator:
    """Execute a primary operation and run a secondary validation step."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.validator = SecondaryCopilotValidator(self.logger)

    def run(
        self,
        main_op: Callable[..., Any],
        *args: Any,
        files: Iterable[str] | None = None,
        **kwargs: Any,
    ) -> tuple[Any, bool]:
        """Run ``main_op`` and validate the result with flake8."""

        result = main_op(*args, **kwargs)
        validated = self.validator.validate_corrections(list(files or []))
        if validated:
            self.logger.info("Dual validation succeeded")
        else:
            self.logger.error("Dual validation failed")
        return result, validated


__all__ = ["DualCopilotOrchestrator"]
