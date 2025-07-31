#!/usr/bin/env python3
"""Session Artifact Management Module.

This utility detects new or modified files within ``tmp/`` since the last
commit, compresses them into a timestamped archive and stores the result in
``codex_sessions/``. Paths can be customized via ``.codex_lfs_policy.yaml`` with
``tmp_dir`` and ``sessions_dir`` keys.
"""

from __future__ import annotations

import logging
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List

import yaml

from utils.enterprise_logging import setup_logging

__all__ = ["create_session_archive"]

logger = setup_logging(module_name=__name__)


def _load_policy() -> dict:
    """Load `.codex_lfs_policy.yaml` if present."""
    policy_path = Path(".codex_lfs_policy.yaml")
    if not policy_path.exists():
        return {}
    try:
        with policy_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load policy %s: %s", policy_path, exc)
        return {}


def _detect_modified(tmp_dir: Path) -> List[Path]:
    """Return files created or modified under ``tmp_dir`` since last commit."""
    files: set[Path] = set()
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", str(tmp_dir)],
            check=False,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line:
                files.add(Path(line))
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to detect untracked files: %s", exc)

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", str(tmp_dir)],
            check=False,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line:
                files.add(Path(line))
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to detect modified files: %s", exc)

    existing_files = [f.resolve() for f in files if f.exists()]
    logger.info("Detected %s modified/untracked files", len(existing_files))
    return existing_files


def _add_to_zip(zipf: zipfile.ZipFile, base_dir: Path, file_path: Path) -> None:
    if file_path.is_file():
        arcname = file_path.relative_to(base_dir)
        zipf.write(file_path, arcname=arcname)
    elif file_path.is_dir():
        for sub in file_path.rglob("*"):
            if sub.is_file():
                arcname = sub.relative_to(base_dir)
                zipf.write(sub, arcname=arcname)


def create_session_archive() -> Path | None:
    """Create a zip archive of new/modified items in the temporary directory."""
    policy = _load_policy()
    tmp_dir = Path(policy.get("tmp_dir", "tmp"))
    sessions_dir = Path(policy.get("sessions_dir", "codex_sessions"))

    if not tmp_dir.exists():
        logger.warning("Temporary directory %s does not exist", tmp_dir)
        return None

    sessions_dir.mkdir(parents=True, exist_ok=True)

    files = _detect_modified(tmp_dir)
    if not files:
        logger.info("No session artifacts detected")
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_name = f"codex-session_{timestamp}.zip"
    archive_path = sessions_dir / archive_name

    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                _add_to_zip(zipf, tmp_dir, file_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create archive %s: %s", archive_path, exc)
        return None

    logger.info("Created session archive %s", archive_path)
    return archive_path


if __name__ == "__main__":
    create_session_archive()
