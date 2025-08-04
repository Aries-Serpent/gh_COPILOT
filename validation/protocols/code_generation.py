from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Callable, Tuple

from utils.logging_utils import log_dual_validation_outcome
from ..core.validators import BaseValidator, ValidationResult, ValidationStatus


class DBFirstGenerationValidator(BaseValidator):
    """Validate DB-first generation events are logged."""

    def __init__(self, analytics_db: Path, objective: str) -> None:
        super().__init__("DB-First Generation Validator")
        self.analytics_db = Path(analytics_db)
        self.objective = objective

    def validate(self, target: object = None) -> ValidationResult:
        if not self.analytics_db.exists():
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"analytics db not found: {self.analytics_db}",
            )
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM code_generation_events WHERE objective = ?",
                    (self.objective,),
                )
                count = cur.fetchone()[0]
            status = ValidationStatus.PASSED if count > 0 else ValidationStatus.FAILED
            msg = "generation event logged" if count > 0 else "missing generation event"
            return ValidationResult(status=status, message=msg, details={"count": count})
        except Exception as exc:  # pragma: no cover - error path
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"validation error: {exc}",
                errors=[str(exc)],
            )


def run_dual_validation(
    primary: Callable[[], Any], secondary: Callable[[], Any]
) -> Tuple[Any, Any]:
    """Execute primary and secondary copilots sequentially and log outcomes."""
    primary_result = primary()
    secondary_result = secondary()
    log_dual_validation_outcome(primary_result, secondary_result)
    return primary_result, secondary_result
