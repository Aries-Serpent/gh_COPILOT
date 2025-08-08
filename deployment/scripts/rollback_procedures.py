from __future__ import annotations

"""Rollback utilities for the web GUI and quantum modules.

Adjusted to use the new ``web_gui`` directory location at the repository root
and restore both production and quantum databases.
"""

from pathlib import Path
import os

from .restoration_engine import restore_backup
from .quantum_migration import migrate_quantum

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"


def rollback() -> None:
    """Simulate rolling back the web GUI and quantum modules."""
    restore_backup("production")
    restore_backup("quantum")
    migrate_quantum()
    print(f"Rolling back web GUI using artifacts in {WEB_GUI_PATH}")


if __name__ == "__main__":
    rollback()
