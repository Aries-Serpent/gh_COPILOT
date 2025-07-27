"""Enterprise operation validation helpers."""

from __future__ import annotations

import os
from pathlib import Path


def validate_enterprise_operation(path: str | None = None) -> bool:
    """Validate operations to prevent internal backup access."""

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())).resolve()
    target = Path(path or workspace).resolve()
    backup_root = Path(
        os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups")
    ).resolve()

    if backup_root == workspace or backup_root.is_relative_to(workspace):
        raise RuntimeError("Backup root cannot be inside the workspace")

    if target.is_relative_to(workspace) and "backup" in target.name.lower():
        raise RuntimeError("Operations targeting internal backups are forbidden")

    return True

