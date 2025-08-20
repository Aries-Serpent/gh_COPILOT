"""Global test configuration.

This file installs a lightweight PyQt6 stub when the real library is
absent so that tests depending on PyQt6 can run in headless
environments.
"""

from __future__ import annotations

import sys


try:  # Prefer real PyQt6 when available
    import PyQt6  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    from tests.stubs import pyqt6 as PyQt6

    # Register stub modules so ``import PyQt6`` succeeds
    sys.modules.setdefault("PyQt6", PyQt6)
    sys.modules.setdefault("PyQt6.QtCore", PyQt6.QtCore)
    sys.modules.setdefault("PyQt6.QtWidgets", PyQt6.QtWidgets)

__all__ = ["PyQt6"]

