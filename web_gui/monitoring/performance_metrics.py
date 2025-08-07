"""Collect performance metrics for the web GUI."""

from __future__ import annotations

import psutil
from typing import Dict

__all__ = ["collect_performance_metrics"]


def collect_performance_metrics() -> Dict[str, float]:
    """Return basic system performance metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
    }
