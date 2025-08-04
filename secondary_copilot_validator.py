"""Compatibility wrapper exposing secondary validation utilities."""

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator
from utils.validation_utils import run_dual_copilot_validation

__all__ = ["SecondaryCopilotValidator", "run_dual_copilot_validation"]
