"""Automation package.

Exposes core orchestration dataclasses and helpers.
"""

from .core import (
    StepCtx,
    ExecutionResult,
    RunArtifacts,
    run_phases,
)

__all__ = [
    "StepCtx",
    "ExecutionResult",
    "RunArtifacts",
    "run_phases",
]

