from __future__ import annotations

import sqlite3
from pathlib import Path

from ..core.validators import BaseValidator, ValidationResult, ValidationStatus


class DocumentationManagerValidator(BaseValidator):
    """Validate documentation render events are logged."""

    def __init__(self, analytics_db: Path) -> None:
        super().__init__("Documentation Manager Validator")
        self.analytics_db = Path(analytics_db)

    def validate(self, target: object = None) -> ValidationResult:
        if not self.analytics_db.exists():
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"analytics db not found: {self.analytics_db}",
            )
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cur = conn.execute("SELECT COUNT(*) FROM render_events")
                count = cur.fetchone()[0]
            status = ValidationStatus.PASSED if count > 0 else ValidationStatus.FAILED
            msg = "render events logged" if count > 0 else "no render events"
            return ValidationResult(status=status, message=msg, details={"count": count})
        except Exception as exc:  # pragma: no cover - error path
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"validation error: {exc}",
                errors=[str(exc)],
            )
