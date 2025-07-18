"""File utilities for gh_COPILOT Enterprise Toolkit"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union


def read_file_safely(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Read file with safe encoding handling"""
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception:
        return None


def write_file_safely(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Write file with safe error handling"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def copy_file_safely(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy file with safe error handling"""
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def quarantine_zero_byte_files(
    target_dir: Union[str, Path], quarantine_dir: Union[str, Path]
) -> int:
    """Move zero-byte files from ``target_dir`` to ``quarantine_dir``."""
    target = Path(target_dir)
    quarantine = Path(quarantine_dir)
    quarantine.mkdir(parents=True, exist_ok=True)
    moved = 0
    for file_path in target.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0:
            try:
                file_path.replace(quarantine / file_path.name)
                moved += 1
            except Exception:
                continue
    return moved
