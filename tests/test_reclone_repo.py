"""Tests for reclone_repo.py utility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "reclone_repo.py"


def _create_repo(tmp_path: Path) -> Path:
    """Create a simple git repository and return its path."""
    origin = tmp_path / "origin"
    subprocess.check_call(["git", "init", "-b", "main", origin])
    (origin / "file.txt").write_text("content", encoding="utf-8")
    subprocess.check_call(["git", "-C", origin, "add", "file.txt"])
    subprocess.check_call(["git", "-C", origin, "commit", "-m", "init"])
    return origin


def test_clone_basic(tmp_path: Path) -> None:
    origin = _create_repo(tmp_path)
    dest = tmp_path / "clone"

    result = subprocess.check_output(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-url",
            str(origin),
            "--dest",
            str(dest),
        ],
        text=True,
    ).strip()

    expected = subprocess.check_output(
        ["git", "-C", str(origin), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    assert result == expected
    assert (dest / "file.txt").exists()


def test_backup_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    origin = _create_repo(tmp_path)
    dest = tmp_path / "clone"
    dest.mkdir()
    (dest / "old.txt").write_text("old", encoding="utf-8")
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    subprocess.check_call(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-url",
            str(origin),
            "--dest",
            str(dest),
            "--backup-existing",
        ]
    )

    backups = list(backup_root.iterdir())
    assert len(backups) == 1
    assert (backups[0] / "old.txt").exists()
    assert (dest / "file.txt").exists()


def test_backup_env_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    origin = _create_repo(tmp_path)
    dest = tmp_path / "clone"
    dest.mkdir()

    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-url",
            str(origin),
            "--dest",
            str(dest),
            "--backup-existing",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "GH_COPILOT_BACKUP_ROOT" in proc.stderr
