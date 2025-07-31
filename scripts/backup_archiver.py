#!/usr/bin/env python3
"""Archive backups using 7z compression."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import py7zr

from enterprise_modules.compliance import validate_enterprise_operation
from utils.cross_platform_paths import CrossPlatformPathManager


def archive_backups() -> Path:
    """Compress backup files and store the archive under ``archive/``."""

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
    return archive_path


if __name__ == "__main__":  # pragma: no cover - manual invocation
    archive_backups()
