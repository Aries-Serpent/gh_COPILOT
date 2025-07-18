"""Compress enterprise assets backups into the approved backup directory."""
from __future__ import annotations

import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path, PureWindowsPath

from scripts.continuous_operation_orchestrator import \
    validate_enterprise_operation

logger = logging.getLogger(__name__)

DEFAULT_BACKUP_ROOT = (
    Path("E:/temp/gh_COPILOT_Backups") if os.name == "nt" else Path("/temp/gh_COPILOT_Backups")
)
BACKUP_ROOT = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", str(DEFAULT_BACKUP_ROOT)))


def _resolve(path: Path | str) -> Path:
    return Path(path).resolve()


def _ensure_valid_destination(dest: Path, workspace: Path) -> None:
    dest = dest.resolve()
    workspace = workspace.resolve()
    try:
        dest.relative_to(BACKUP_ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Backups must reside under {BACKUP_ROOT}") from exc
    try:
        dest.relative_to(workspace)
        raise RuntimeError("Backup location cannot be within the workspace")
    except ValueError:
        pass


def compress_assets_backup(workspace: Path | str, source_dir: Path | str, backup_name: str | None = None) -> Path:
    """Compress ``source_dir`` into a zip archive under ``BACKUP_ROOT``.

    Parameters
    ----------
    workspace:
        Root of the workspace being backed up.
    source_dir:
        Directory containing assets to compress.
    backup_name:
        Optional name of the resulting archive. If omitted a timestamped name is used.
    """
    validate_enterprise_operation()
    workspace = _resolve(workspace)
    source_dir = _resolve(source_dir)

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    backup_dir = BACKUP_ROOT / workspace.name
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_name = backup_name or f"assets_backup_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.zip"
    dest_zip = backup_dir / backup_name

    _ensure_valid_destination(dest_zip, workspace)

    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in source_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(source_dir))
    logger.info("Backup created: %s", dest_zip)
    return dest_zip
