"""Compatibility namespace for monitoring modules.

This package exposes the implementation from :mod:`src.monitoring` so
imports like ``from monitoring.anomaly import StatisticalAnomalyDetector``
continue to work without installing the package.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import sys

# Add the src/monitoring directory to this package's search path so that
# submodules are resolved from the original implementation.
_src_path = Path(__file__).resolve().parent.parent / "src" / "monitoring"
if _src_path.is_dir():
    __path__.append(str(_src_path))

    # Load the original package to re-export its public API.
    _spec = spec_from_file_location(
        "_monitoring_impl",
        _src_path / "__init__.py",
        submodule_search_locations=[str(_src_path)],
    )
    if _spec and _spec.loader:  # pragma: no cover - defensive
        _impl: ModuleType = module_from_spec(_spec)
        sys.modules.setdefault("_monitoring_impl", _impl)
        _spec.loader.exec_module(_impl)
        __all__ = getattr(_impl, "__all__", [])
        for _name in __all__:
            globals()[_name] = getattr(_impl, _name)
else:  # pragma: no cover - fallback when src tree missing
    __all__: list[str] = []
