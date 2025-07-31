"""Utility for packaging session artifacts.

Detects changed files in ``tmp/`` since the last commit and archives them into a
timestamped zip file under ``codex_sessions/``. Git LFS tracking is applied if
enabled via ``.codex_lfs_policy.yaml``.
"""

from __future__ import annotations

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


def package_session(tmp_dir: Path, repo_root: Path, lfs_policy: Optional[LfsPolicy] = None) -> Optional[Path]:
    changed_files = detect_tmp_changes(tmp_dir, repo_root)
    if not changed_files:
        logger.info("No session artifacts detected in %s", tmp_dir)
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"codex-session_{timestamp}.zip"

    sessions_dir = repo_root / "codex_sessions"
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

    return archive_path


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    repo_root = Path(__file__).resolve().parent
    tmp_dir = repo_root / "tmp"
    policy = LfsPolicy(repo_root)
    package_session(tmp_dir, repo_root, policy)


if __name__ == "__main__":
    main()
