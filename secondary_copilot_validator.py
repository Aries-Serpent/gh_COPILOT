"""Compatibility wrapper exposing validation utilities.

This module now also provides access to the enterprise compliance validator
which aggregates analytics metrics into a composite score.
"""

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator
from utils.validation_utils import run_dual_copilot_validation
from validation.enterprise_compliance_validator import EnterpriseComplianceValidator


def run_flake8(files: list[str]) -> bool:
    """Run secondary flake8 validation on ``files``.

    This convenience wrapper aligns with the dual-copilot pattern by
    delegating to :class:`SecondaryCopilotValidator` after code generation
    or modification steps.
    """

    validator = SecondaryCopilotValidator()
    return validator.validate_corrections(files)


def record_compliance_metrics() -> float:
    """Collect and persist a composite compliance score.

    The returned value represents the composite score computed from lint,
    test, placeholder, and session metrics stored in ``analytics.db``.
    """

    validator = EnterpriseComplianceValidator()
    result = validator.evaluate()
    return result["composite_score"]


__all__ = [
    "SecondaryCopilotValidator",
    "run_dual_copilot_validation",
    "run_flake8",
    "EnterpriseComplianceValidator",
    "record_compliance_metrics",
]
