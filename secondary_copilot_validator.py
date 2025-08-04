"""Compatibility wrapper exposing secondary validation utilities."""

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator
from utils.validation_utils import run_dual_copilot_validation


def run_flake8(files: list[str]) -> bool:
    """Run secondary flake8 validation on ``files``.

    This convenience wrapper aligns with the dual-copilot pattern by
    delegating to :class:`SecondaryCopilotValidator` after code generation
    or modification steps.
    """

    validator = SecondaryCopilotValidator()
    return validator.validate_corrections(files)


__all__ = [
    "SecondaryCopilotValidator",
    "run_dual_copilot_validation",
    "run_flake8",
]
