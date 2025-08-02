"""Thin wrapper for :mod:"scripts.database.database_first_windows_compatible_flake8_corrector"."""

from scripts.database.database_first_windows_compatible_flake8_corrector import (
    CorrectionPattern,
    DatabaseFirstFlake8Corrector,
    FlakeViolation,
)

__all__ = ["CorrectionPattern", "DatabaseFirstFlake8Corrector", "FlakeViolation"]
