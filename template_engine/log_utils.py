"""Backward-compatibility wrapper for :mod:`utils.log_utils`.

This module re-exports :func:`utils.log_utils._log_event` for older imports.
All new code should import from ``utils.log_utils`` instead.
"""

from utils.log_utils import _log_event

__all__ = ["_log_event"]
