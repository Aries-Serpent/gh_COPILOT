"""Utility for packaging and recovering session artifacts.

This module detects changed files within a temporary directory, archives them
into a timestamped zip stored under ``codex_sessions/`` and optionally tracks
the archive via Git LFS based on ``.codex_lfs_policy.yaml``. Created archives
are automatically committed to the repository. The module also provides a
recovery helper to extract the most recent session archive back into the
temporary directory.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from zipfile import ZipFile

import yaml


logger = logging.getLogger(__name__)


class LfsPolicy:
    """Configuration for Git LFS compliance."""

    def __init__(self, root: Path) -> None:
        self.enabled = False
        self.size_threshold_mb = 50
        self.binary_extensions: List[str] = [
            ".db",
            ".7z",
            ".zip",
            ".bak",
            ".dot",
            ".sqlite",
            ".exe",
        ]
        self.session_artifact_dir = "codex_sessions"
        self.root = root

        policy_file = root / ".codex_lfs_policy.yaml"
        if policy_file.exists():
            try:
                data = yaml.safe_load(policy_file.read_text()) or {}
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to read %s: %s", policy_file, exc)
            else:
                self.enabled = bool(data.get("enable_autolfs", False))
                self.size_threshold_mb = int(data.get("size_threshold_mb", 50))
                self.binary_extensions = list(data.get("binary_extensions", self.binary_extensions))
                self.session_artifact_dir = str(data.get("session_artifact_dir", self.session_artifact_dir)).rstrip("/")

    def requires_lfs(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if path.suffix in self.binary_extensions:
            return True
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb > self.size_threshold_mb

    def track(self, path: Path) -> None:
        if not self.enabled:
            logger.debug("LFS auto tracking disabled.")
            return
        try:
            subprocess.run(["git", "lfs", "install"], cwd=self.root, check=True, capture_output=True)
            subprocess.run(["git", "lfs", "track", path.name], cwd=self.root, check=True, capture_output=True)
            git_attr = self.root / ".gitattributes"
            if git_attr.exists():
                subprocess.run(["git", "add", str(git_attr)], cwd=self.root, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:  # noqa: BLE001
            logger.error("Failed to set up Git LFS tracking: %s", exc)


def _run_git(cmd: Iterable[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True)


def commit_archive(repo_root: Path, archive_path: Path) -> bool:
    """Commit the created archive to Git.

    Parameters
    ----------
    repo_root:
        Root directory of the repository.
    archive_path:
        Path to the zip archive to commit.
    """
    try:
        subprocess.run(["git", "add", str(archive_path)], cwd=repo_root, check=True, capture_output=True)
        subprocess.run([
            "git",
            "commit",
            "-m",
            f"chore: add session archive {archive_path.name}",
        ], cwd=repo_root, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        logger.error("Failed to commit archive: %s", exc)
        return False
    return True


def detect_tmp_changes(tmp_dir: Path, repo_root: Path) -> List[Path]:
    if not tmp_dir.exists():
        logger.info("Temporary directory %s does not exist.", tmp_dir)
        return []

    try:
        output = _run_git(["status", "--porcelain", str(tmp_dir)], cwd=repo_root)
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        logger.error("git status failed: %s", exc)
        return []

    changed: List[Path] = []
    for line in output.splitlines():
        status, file_path = line[:2], line[3:]
        if status.strip() in {"M", "A", "??"}:
            changed.append(repo_root / file_path)
    return changed


def create_zip(archive_path: Path, files: Iterable[Path], base_dir: Path) -> None:
    with ZipFile(archive_path, "w") as zf:
        for file in files:
            if file.exists():
                zf.write(file, arcname=file.relative_to(base_dir))


def recover_latest_session(
    tmp_dir: Path, repo_root: Path, lfs_policy: Optional[LfsPolicy] = None
) -> Optional[Path]:
    """Extract the most recent session archive into ``tmp_dir``.

    Parameters
    ----------
    tmp_dir:
        Directory where files will be restored.
    repo_root:
        Root directory of the repository containing ``codex_sessions``.
    """
    sessions_dir = repo_root / (
        lfs_policy.session_artifact_dir if lfs_policy else "codex_sessions"
    )
    if not sessions_dir.exists():
        logger.info("No session archives found at %s", sessions_dir)
        return None
    archives = sorted(sessions_dir.glob("codex-session_*.zip"), reverse=True)
    if not archives:
        logger.info("No session archives present in %s", sessions_dir)
        return None
    latest = archives[0]
    try:
        with ZipFile(latest, "r") as zf:
            zf.extractall(repo_root)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract %s: %s", latest, exc)
        return None
    logger.info("Recovered session from %s", latest)
    return latest


def package_session(tmp_dir: Path, repo_root: Path, lfs_policy: Optional[LfsPolicy] = None) -> Optional[Path]:
    """Archive new/modified files from ``tmp_dir`` and commit the archive."""

    changed_files = detect_tmp_changes(tmp_dir, repo_root)
    if not changed_files:
        logger.info("No session artifacts detected in %s", tmp_dir)
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"codex-session_{timestamp}.zip"

    sessions_dir = repo_root / (
        lfs_policy.session_artifact_dir if lfs_policy else "codex_sessions"
    )
    sessions_dir.mkdir(parents=True, exist_ok=True)

    archive_path = sessions_dir / archive_name

    try:
        create_zip(archive_path, changed_files, repo_root)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create archive: %s", exc)
        return None

    logger.info("Created session archive %s", archive_path)

    if lfs_policy and lfs_policy.requires_lfs(archive_path):
        lfs_policy.track(archive_path)

    commit_archive(repo_root, archive_path)

    return archive_path


def recover_latest_session(tmp_dir: Path, repo_root: Path) -> Optional[Path]:
    """Extract the most recent session archive back into ``tmp_dir``."""
    sessions_dir = repo_root / "codex_sessions"
    if not sessions_dir.exists():
        logger.info("Sessions directory %s does not exist", sessions_dir)
        return None

    archives = sorted(sessions_dir.glob("codex-session_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not archives:
        logger.info("No session archives found in %s", sessions_dir)
        return None

    latest = archives[0]
    try:
        with ZipFile(latest, "r") as zf:
            zf.extractall(repo_root)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract archive %s: %s", latest, exc)
        return None

    logger.info("Recovered session archive %s", latest)
    return latest


def main() -> None:
    """Entry point for CLI usage."""

    parser = argparse.ArgumentParser(description="Manage session artifacts")
    parser.add_argument(
        "--tmp-dir",
        type=Path,
        default=Path("tmp"),
        help="Temporary directory containing artifacts",
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Recover the latest session archive instead of packaging",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    repo_root = Path(__file__).resolve().parent
    policy = LfsPolicy(repo_root)

    if args.recover:
        recover_latest_session(args.tmp_dir, repo_root, policy)
    else:
        package_session(args.tmp_dir, repo_root, policy)


if __name__ == "__main__":
    main()
