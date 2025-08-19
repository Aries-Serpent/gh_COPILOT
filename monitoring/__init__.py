"""Compatibility namespace for monitoring modules.

This package exposes the implementation from :mod:`src.monitoring` so
imports like ``from monitoring.anomaly import StatisticalAnomalyDetector``
continue to work without installing the package.
"""

from __future__ import annotations

from pathlib import Path

# Add the src/monitoring directory to this package's search path so that
# submodules are resolved from the original implementation.
_src_path = Path(__file__).resolve().parent.parent / "src" / "monitoring"
if _src_path.is_dir():
    __path__.append(str(_src_path))
