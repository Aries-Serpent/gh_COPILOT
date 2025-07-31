import os
import subprocess
from pathlib import Path

from artifact_manager import (
    LfsPolicy,
    package_session,
    recover_latest_session,
)


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "tmp").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True)
    policy = repo / ".codex_lfs_policy.yaml"
    policy.write_text(
        """\
# Enable or disable the automatic Git LFS tracking logic
enable_autolfs: true
session_artifact_dir: "codex_sessions"
size_threshold_mb: 1
binary_extensions:
  - .zip
"""
    )
    git_attr = repo / ".gitattributes"
    git_attr.write_text("codex_sessions/*.zip filter=lfs diff=lfs merge=lfs -text\n")
    subprocess.run(["git", "add", str(policy), str(git_attr)], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)
    return repo


def test_package_and_recover(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    tmp_dir = repo / "tmp"
    test_file = tmp_dir / "example.txt"
    test_file.write_text("data")
    subprocess.run(["git", "add", str(test_file)], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "add tmp file"], cwd=repo, check=True)
    test_file.write_text("update")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive and archive.exists()

    # verify committed
    log = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=repo, text=True)
    assert "session archive" in log

    # ensure lfs tracking
    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name in lfs_files

    # remove tmp file and recover
    os.remove(test_file)
    recover_latest_session(tmp_dir, repo, policy)
    assert test_file.exists()


def test_no_changes(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    policy = LfsPolicy(repo)
    tmp_dir = repo / "tmp"
    result = package_session(tmp_dir, repo, policy)
    assert result is None


def test_missing_tmp(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    policy = LfsPolicy(repo)
    tmp_dir = repo / "absent"
    result = package_session(tmp_dir, repo, policy)
    assert result is None
