"""Utility for packaging session artifacts.

Detects changed files in ``tmp/`` since the last commit and archives them into a
timestamped zip file under ``codex_sessions/``. Git LFS tracking is applied if
enabled via ``.codex_lfs_policy.yaml``.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime, timezone
import argparse
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
                subprocess.run(["git", "add", git_attr.name], cwd=self.root, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:  # noqa: BLE001
            logger.error("Failed to set up Git LFS tracking: %s", exc)


def detect_tmp_changes(tmp_dir: Path, repo_root: Path) -> List[Path]:
    """Return all files under ``tmp_dir`` relative to ``repo_root``."""

    if not tmp_dir.exists():
        logger.info("Temporary directory %s does not exist.", tmp_dir)
        return []

    return [p for p in tmp_dir.rglob("*") if p.is_file()]


def create_zip(archive_path: Path, files: Iterable[Path], base_dir: Path) -> None:
    with ZipFile(archive_path, "w") as zf:
        for file in files:
            if file.exists():
                zf.write(file, arcname=file.relative_to(base_dir))


def package_session(
    tmp_dir: Path,
    repo_root: Path,
    lfs_policy: Optional[LfsPolicy] = None,
    *,
    commit: bool = False,
    message: str | None = None,
) -> Optional[Path]:
    """Package changed files in ``tmp_dir`` into a ZIP archive.

    Parameters
    ----------
    tmp_dir:
        Temporary directory containing session outputs.
    repo_root:
        Root of the git repository.
    lfs_policy:
        Optional :class:`LfsPolicy` for Git LFS enforcement.
    commit:
        If ``True``, commit the created archive to git.
    message:
        Optional commit message. If not provided, a default message using the
        archive timestamp is used.

    Returns
    -------
    Optional[Path]
        Path to the created archive or ``None`` if no changes detected.
    """

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

    if commit:
        try:
            subprocess.run(["git", "add", str(archive_path.relative_to(repo_root))], cwd=repo_root, check=True)
            try:
                tracked = subprocess.check_output(
                    ["git", "lfs", "ls-files", str(archive_path.name)], cwd=repo_root, text=True
                )
            except subprocess.CalledProcessError:
                tracked = ""
            if lfs_policy and lfs_policy.enabled and not tracked.strip():
                logger.error("Archive %s is not tracked by Git LFS", archive_path)
            commit_msg = message or f"Add session artifact {timestamp}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=repo_root,
                check=True,
            )
            logger.info("Committed archive %s", archive_path)
        except subprocess.CalledProcessError as exc:  # noqa: BLE001
            logger.error("Failed to commit archive: %s", exc)

    return archive_path


def recover_latest_session(tmp_dir: Path, repo_root: Path) -> Optional[Path]:
    """Restore files from the most recent session archive.

    Parameters
    ----------
    tmp_dir:
        Destination directory for extracted files.
    repo_root:
        Root of the git repository containing ``codex_sessions``.

    Returns
    -------
    Optional[Path]
        Path to the extracted archive or ``None`` if none found.
    """

    sessions_dir = repo_root / "codex_sessions"
    if not sessions_dir.exists():
        logger.warning("%s does not exist", sessions_dir)
        return None

    archives = sorted(sessions_dir.glob("codex-session_*.zip"), reverse=True)
    if not archives:
        logger.warning("No session archives found in %s", sessions_dir)
        return None

    archive = archives[0]
    try:
        with ZipFile(archive) as zf:
            zf.extractall(tmp_dir)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract %s: %s", archive, exc)
        return None

    logger.info("Recovered session from %s", archive)
    return archive


def main() -> None:
    """Command-line interface for session packaging and recovery."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", action="store_true", help="create session archive")
    parser.add_argument("--recover", action="store_true", help="recover latest session")
    parser.add_argument("--commit", action="store_true", help="commit created archive")
    parser.add_argument("--message", help="commit message when packaging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    repo_root = Path(__file__).resolve().parent
    tmp_dir = repo_root / "tmp"
    policy = LfsPolicy(repo_root)

    if args.package:
        package_session(
            tmp_dir,
            repo_root,
            policy,
            commit=args.commit,
            message=args.message,
        )

    if args.recover:
        recover_latest_session(tmp_dir, repo_root)


if __name__ == "__main__":
    main()
