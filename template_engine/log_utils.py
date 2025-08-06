"""Backward-compatibility wrapper for :mod:`utils.log_utils`.

This module re-exports :func:`utils.log_utils._log_event` for older imports.
All new code should import from ``utils.log_utils`` instead.
"""

import logging
from utils.log_utils import _log_event
from utils.lessons_learned_integrator import load_lessons, apply_lessons

__all__ = ["_log_event"]

apply_lessons(logging.getLogger(__name__), load_lessons())
