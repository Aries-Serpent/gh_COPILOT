import os
import subprocess
from pathlib import Path

import validate_git_operations


def _create_repo(tmp_path: Path, configure_lfs: bool = True) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    if configure_lfs:
        subprocess.run(["git", "config", "lfs.skipdownloaderrors", "true"], cwd=tmp_path, check=True)


def test_validate_git_operations_success(tmp_path):
    _create_repo(tmp_path)
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert validate_git_operations.validate_git_operations() is True
        count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert count == "2"
    finally:
        os.chdir(cwd)


def test_validate_git_operations_failure(tmp_path):
    _create_repo(tmp_path, configure_lfs=False)
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert validate_git_operations.validate_git_operations(dry_run=True) is False
    finally:
        os.chdir(cwd)


def test_validate_git_operations_dry_run(tmp_path):
    _create_repo(tmp_path)
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert validate_git_operations.validate_git_operations(dry_run=True) is True
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        count = result.stdout.strip() if result.returncode == 0 else "0"
        assert count == "0"
    finally:
        os.chdir(cwd)

