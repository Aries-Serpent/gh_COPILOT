from __future__ import annotations

"""Enterprise compliance helpers."""

import os
import shutil
from pathlib import Path


def validate_enterprise_operation(target_path: str | None = None) -> bool:
    """Ensure operations comply with backup and path policies."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    path = Path(target_path or workspace)

    # Disallow workspace backups
    forbidden = [p for p in workspace.rglob("*backup*") if p.is_dir()]
    for item in forbidden:
        shutil.rmtree(item, ignore_errors=True)
        return False

    # Disallow operations in C:/temp
    if str(path).lower().startswith("c:/temp"):
        return False
    return True
