from __future__ import annotations

"""Rollback utilities for the web GUI deployment.

Adjusted to use the new ``web_gui`` directory location at the repository root.
"""

from pathlib import Path
import os

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"


def rollback() -> None:
    """Simulate rolling back the web GUI deployment."""
    print(f"Rolling back web GUI using artifacts in {WEB_GUI_PATH}")


if __name__ == "__main__":
    rollback()
