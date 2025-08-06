from __future__ import annotations

import json
from pathlib import Path

from ..core.validators import BaseValidator, ValidationResult, ValidationStatus


class DashboardMetricsValidator(BaseValidator):
    """Validate dashboard metrics status."""

    def __init__(self, dashboard_dir: Path) -> None:
        super().__init__("Dashboard Metrics Validator")
        self.dashboard_file = Path(dashboard_dir) / "metrics.json"

    def validate(self, target: object = None) -> ValidationResult:
        if not self.dashboard_file.exists():
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"metrics file missing: {self.dashboard_file}",
            )
        try:
            data = json.loads(self.dashboard_file.read_text(encoding="utf-8"))
            status_str = data.get("status")
            result_status = ValidationStatus.PASSED if status_str == "complete" else ValidationStatus.WARNING
            return ValidationResult(
                status=result_status,
                message=f"dashboard status: {status_str}",
                details={"status": status_str},
            )
        except Exception as exc:  # pragma: no cover - error path
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"validation error: {exc}",
                errors=[str(exc)],
            )
