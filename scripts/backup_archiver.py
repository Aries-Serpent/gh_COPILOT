#!/usr/bin/env python3
"""Archive backups using 7z compression."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import py7zr

from enterprise_modules.compliance import (
    enforce_anti_recursion,
    pid_recursion_guard,
    validate_enterprise_operation,
)
from utils.cross_platform_paths import CrossPlatformPathManager
from utils.validation_utils import anti_recursion_guard
from secondary_copilot_validator import (
    SecondaryCopilotValidator,
    run_dual_copilot_validation,
)

__all__ = ["archive_backups", "pid_recursion_guard"]

_RECURSION_CTX = SimpleNamespace()

@pid_recursion_guard
@anti_recursion_guard
def archive_backups() -> Path:
    """Compress backup files and store the archive under ``archive/``."""
    enforce_anti_recursion(_RECURSION_CTX)
    try:
        workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())).resolve()
        backup_root = CrossPlatformPathManager.get_backup_root().resolve()

        if not validate_enterprise_operation(str(workspace)):
            raise RuntimeError("Invalid workspace or backup configuration")

        archive_dir = workspace / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"backups_{timestamp}.7z"

        with py7zr.SevenZipFile(archive_path, "w") as zf:
            for item in backup_root.rglob("*"):
                if item.is_file():
                    zf.write(item, item.relative_to(backup_root))

        logging.info("Archived backups to %s", archive_path)

        validator = SecondaryCopilotValidator()

        def _primary() -> bool:
            return archive_path.exists()

        def _secondary() -> bool:
            return validator.validate_corrections([], primary_success=True)

        run_dual_copilot_validation(_primary, _secondary)
        return archive_path
    finally:
        if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
            _RECURSION_CTX.recursion_depth -= 1
            ancestors = getattr(_RECURSION_CTX, "ancestors", [])
            if ancestors:
                ancestors.pop()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    archive_backups()
