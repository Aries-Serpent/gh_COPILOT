"""File utilities for gh_COPILOT Enterprise Toolkit"""

import shutil
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def read_file_safely(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """Read file with safe encoding handling"""
    try:
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            return f.read()
    except OSError as exc:
        logger.error("Failed to read %s: %s", file_path, exc)
        return None


def write_file_safely(file_path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
    """Write file with safe error handling"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except OSError as exc:
        logger.error("Failed to write %s: %s", file_path, exc)
        return False


def copy_file_safely(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy file with safe error handling"""
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except OSError as exc:
        logger.error("Failed to copy %s to %s: %s", src, dst, exc)
        return False


def quarantine_zero_byte_files(target_dir: Union[str, Path], quarantine_dir: Union[str, Path]) -> int:
    """Move zero-byte files from ``target_dir`` to ``quarantine_dir``."""
    target = Path(target_dir)
    quarantine = Path(quarantine_dir)
    quarantine.mkdir(parents=True, exist_ok=True)
    moved = 0
    for file_path in target.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0:
            try:
                relative_path = file_path.relative_to(target)
                destination = quarantine / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                file_path.replace(destination)
                moved += 1
            except OSError as exc:
                logger.warning("Could not move %s: %s", file_path, exc)
                continue
    return moved
