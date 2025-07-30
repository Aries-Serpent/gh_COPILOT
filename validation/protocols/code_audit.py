from __future__ import annotations

import sqlite3
from pathlib import Path

from ..core.validators import BaseValidator, ValidationResult, ValidationStatus


class PlaceholderAuditValidator(BaseValidator):
    """Validate placeholder audit results exist."""

    def __init__(self, analytics_db: Path) -> None:
        super().__init__("Placeholder Audit Validator")
        self.analytics_db = Path(analytics_db)

    def validate(self, target: object = None) -> ValidationResult:
        if not self.analytics_db.exists():
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"analytics db not found: {self.analytics_db}",
            )
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cur = conn.execute("SELECT COUNT(*) FROM code_audit_log")
                count = cur.fetchone()[0]
            status = ValidationStatus.PASSED if count > 0 else ValidationStatus.FAILED
            msg = "audit log entries found" if count > 0 else "no audit log entries"
            return ValidationResult(status=status, message=msg, details={"entries": count})
        except Exception as exc:  # pragma: no cover - error path
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"validation error: {exc}",
                errors=[str(exc)],
            )
