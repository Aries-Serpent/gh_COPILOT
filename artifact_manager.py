"""Utility for packaging and recovering session artifacts.

This module detects files within a temporary directory, archives them into a
timestamped zip stored under a configurable *session artifact directory* and
optionally tracks the archive via Git LFS based on ``.codex_lfs_policy.yaml``.
Created archives are automatically committed to the repository. The module also
provides a recovery helper to extract the most recent session archive back into
the temporary directory. The command line interface exposes options such as
``--tmp-dir`` to control the working directory for transient files and
``--sync-gitattributes`` to regenerate the repository's ``.gitattributes`` from
policy. The policy file may specify ``session_artifact_dir`` to override the
default ``codex_sessions`` location used for storing archives.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from zipfile import ZipFile

try:  # pragma: no cover - import guard
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    print("PyYAML is required for artifact management. Install it to continue.", file=sys.stderr)
    raise


logger = logging.getLogger(__name__)


class LfsPolicy:
    """Read and hold Git LFS policy settings.

    The policy is loaded from ``.codex_lfs_policy.yaml`` located at the
    repository root.  Only a handful of keys are recognised and all are optional
    so that new keys can be introduced without breaking older versions.

    The relevant YAML structure is::

        enable_autolfs: true|false
        size_threshold_mb: <int>
        binary_extensions: [".db", ".zip", ...]
        gitattributes_template: |
          pattern filter=lfs diff=lfs merge=lfs -text
        session_artifact_dir: <str>

    ``session_artifact_dir`` controls where session archives are stored.  If the
    key is missing, empty or not a string, the default value ``"codex_sessions"``
    is used.  Future versions may extend this class with explicit schema
    validation or migration utilities.

    Attributes
    ----------
    session_artifact_dir:
        Directory used for storing session artifacts.  Defaults to
        ``"codex_sessions"`` when the configuration is missing or invalid.
    """

    DEFAULT_SESSION_DIR = "codex_sessions"

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
        self.gitattributes_template = ""
        self.session_artifact_dir = self.DEFAULT_SESSION_DIR
        self.root = root

        policy_file = root / ".codex_lfs_policy.yaml"
        try:
            text = policy_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.info("%s not found", policy_file)
            logger.info("Using default LFS policy values")
            return
        except OSError as exc:
            logger.error("Cannot read %s: %s", policy_file, exc)
            logger.info("Using default LFS policy values")
            return

        try:
            data = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:  # noqa: BLE001
            logger.error("Malformed YAML in %s: %s", policy_file, exc)
            logger.info("Using default LFS policy values")
            return

        self.enabled = bool(data.get("enable_autolfs", False))
        self.size_threshold_mb = int(data.get("size_threshold_mb", 50))
        self.binary_extensions = list(
            data.get("binary_extensions", self.binary_extensions)
        )
        self.gitattributes_template = data.get("gitattributes_template", "")

        session_dir = data.get("session_artifact_dir")
        if isinstance(session_dir, str) and session_dir.strip():
            self.session_artifact_dir = session_dir.strip().rstrip("/\\")
            logger.info("Using session artifact directory %s", self.session_artifact_dir)
        else:
            if session_dir is not None:
                logger.warning(
                    "Invalid session_artifact_dir value %r; falling back to %s",
                    session_dir,
                    self.session_artifact_dir,
                )
            else:
                logger.info(
                    "session_artifact_dir not specified; using default %s",
                    self.session_artifact_dir,
                )

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

    def sync_gitattributes(self) -> None:
        """Regenerate .gitattributes from the policy template."""
        if not self.gitattributes_template:
            logger.debug("No gitattributes template defined in policy.")
            return

        attrs_file = self.root / ".gitattributes"
        lines = [
            line.rstrip() for line in self.gitattributes_template.splitlines() if line.strip()
        ]
        patterns = {line.split()[0] for line in lines}

        session_pattern = f"{self.session_artifact_dir}/*.zip"
        if session_pattern not in patterns:
            lines.append(f"{session_pattern} filter=lfs diff=lfs merge=lfs -text")
            patterns.add(session_pattern)

        for ext in self.binary_extensions:
            pattern = f"*{ext}"
            if pattern not in patterns:
                lines.append(f"{pattern} filter=lfs diff=lfs merge=lfs -text")
                patterns.add(pattern)

        content = "# Git LFS rules for binary artifacts\n" + "\n".join(lines) + "\n# End of LFS patterns\n"

        current = attrs_file.read_text(encoding="utf-8") if attrs_file.exists() else ""
        if current.strip() != content.strip():
            attrs_file.write_text(content, encoding="utf-8")
            logger.info("Updated %s", attrs_file)


def detect_tmp_changes(tmp_dir: Path, repo_root: Path) -> List[Path]:
    """Return all files under ``tmp_dir`` relative to ``repo_root``."""

    if not tmp_dir.exists():
        logger.info("Temporary directory %s does not exist.", tmp_dir)
        return []

    return [p for p in tmp_dir.rglob("*") if p.is_file()]


def check_directory_health(dir_path: Path, repo_root: Path) -> bool:
    """Validate that ``dir_path`` is usable for artifact operations.

    The path must be within ``repo_root``, not a symlink and writable.  The
    directory is created if necessary.  Any problem is logged and ``False`` is
    returned so callers can abort their work safely.
    """

    try:
        if dir_path.is_symlink():
            logger.error("Directory %s is a symlink", dir_path)
            return False
        resolved_root = repo_root.resolve()
        resolved = dir_path.resolve()
        repo_root_resolved = repo_root.resolve()
    except OSError as exc:  # pragma: no cover - extremely unusual
        logger.error("Failed to resolve %s: %s", dir_path, exc)
        return False

    try:
        resolved.relative_to(repo_root_resolved)
    except ValueError:
        logger.error("Directory %s escapes repository root", resolved)
        return False

    if dir_path.is_symlink():
        logger.error("Directory %s is a symlink", dir_path)
        return False

    try:
        os.makedirs(resolved, exist_ok=True)
    except OSError as exc:
        logger.error("Failed to create %s: %s", resolved, exc)
        return False

    if not os.access(resolved, os.W_OK):
        logger.error("Directory %s is not writable", resolved)
        return False

    return True


def create_zip(archive_path: Path, files: Iterable[Path], base_dir: Path) -> None:
    """Create ``archive_path`` containing ``files`` relative to ``base_dir``.

    The archive is first written to a temporary file located in the target
    directory and then atomically renamed to ``archive_path``.  This approach
    minimises the risk of leaving partial archives behind if the process is
    interrupted.
    """

    archive_dir = archive_path.parent
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        logger.error("Cannot create directory %s: %s", archive_dir, exc)
        raise

    tmp_file: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".tmp", dir=archive_dir, delete=False
        ) as tf:
            tmp_file = Path(tf.name)
        with ZipFile(tmp_file, "w") as zf:
            for file in files:
                if file.exists():
                    zf.write(file, arcname=file.relative_to(base_dir))
        if archive_path.exists():
            logger.warning("Replacing existing archive %s", archive_path)
        os.replace(tmp_file, archive_path)
    except PermissionError as exc:
        logger.error("Permission denied while creating archive %s: %s", archive_path, exc)
        raise
    except OSError as exc:
        logger.error("Failed to create archive %s: %s", archive_path, exc)
        raise
    finally:
        if tmp_file and tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass


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

    Notes
    -----
    All files packaged into the archive are removed from ``tmp_dir`` to keep the
    temporary workspace clean. The destination directory for archives is
    determined by ``lfs_policy.session_artifact_dir``.  A directory health check
    ensures the target exists within the repository and is writable on all
    supported platforms.
    """

    if lfs_policy is None:
        lfs_policy = LfsPolicy(repo_root)

    changed_files = detect_tmp_changes(tmp_dir, repo_root)
    if not changed_files:
        logger.info("No session artifacts detected in %s", tmp_dir)
        return None

    if not check_directory_health(tmp_dir, repo_root):
        return None

    sessions_dir = repo_root / lfs_policy.session_artifact_dir
    if not check_directory_health(sessions_dir, repo_root):
        return None
    logger.info("Session artifacts directory: %s", sessions_dir)

    timestamp = datetime.now(timezone.utc)
    archive_name = f"codex-session_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
    archive_path = sessions_dir / archive_name
    logger.info(
        "Packaging session: tmp=%s archive_dir=%s time=%s",
        tmp_dir,
        sessions_dir,
        timestamp.isoformat(),
    )

    try:
        create_zip(archive_path, changed_files, tmp_dir)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create archive: %s", exc)
        return None

    # remove processed files to ensure idempotency
    for file in changed_files:
        try:
            file.unlink()
        except FileNotFoundError:
            continue
        parent = file.parent
        while parent != tmp_dir and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent

    logger.info("Created session archive %s", archive_path)

    if lfs_policy and lfs_policy.requires_lfs(archive_path):
        lfs_policy.track(archive_path)

    if commit:
        try:
            subprocess.run(
                ["git", "add", str(archive_path.relative_to(repo_root))],
                cwd=repo_root,
                check=True,
            )
            try:
                tracked = subprocess.check_output(
                    [
                        "git",
                        "lfs",
                        "ls-files",
                        str(archive_path.relative_to(repo_root)),
                    ],
                    cwd=repo_root,
                    text=True,
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


def recover_latest_session(
    tmp_dir: Path, repo_root: Path, lfs_policy: Optional[LfsPolicy] = None
) -> Optional[Path]:
    """Restore files from the most recent session archive.

    Parameters
    ----------
    tmp_dir:
        Destination directory for extracted files.
    repo_root:
        Root of the git repository containing session archives.
    lfs_policy:
        Optional :class:`LfsPolicy` to locate custom session directory.

    Returns
    -------
    Optional[Path]
        Path to the extracted archive or ``None`` if none found.

    Notes
    -----
    The session directory is validated for safety before extraction and must
    reside within the repository root.
    """

    if lfs_policy is None:
        lfs_policy = LfsPolicy(repo_root)

    sessions_dir = repo_root / lfs_policy.session_artifact_dir
    if not check_directory_health(sessions_dir, repo_root):
        return None

    archives = sorted(sessions_dir.glob("codex-session_*.zip"), reverse=True)
    if not archives:
        logger.warning("No session archives found in %s", sessions_dir)
        return None

    archive = archives[0]
    logger.info(
        "Restoring session: archive_dir=%s tmp=%s time=%s",\
        sessions_dir, tmp_dir, datetime.now(timezone.utc).isoformat(),
    )
    try:
        with ZipFile(archive) as zf:
            zf.extractall(tmp_dir)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract %s: %s", archive, exc)
        return None

    logger.info("Recovered session from %s", archive)
    return archive


def main() -> None:
    """Entry point for the artifact manager command line interface.

    ``--tmp-dir`` controls where transient files are gathered for packaging.
    The destination of the resulting archive remains governed by the
    ``session_artifact_dir`` setting in ``.codex_lfs_policy.yaml``.

    When ``--sync-gitattributes`` is supplied, the policy's
    ``gitattributes_template`` and binary extension list are used to
    regenerate the repository's ``.gitattributes`` file.

    Examples
    --------
    Package session files using a custom temporary directory::

        python artifact_manager.py --package --tmp-dir build/tmp

    Regenerate the repository's ``.gitattributes`` file from policy::

        python artifact_manager.py --sync-gitattributes
    """

    examples = (
        "Examples:\n"
        "  python artifact_manager.py --package --tmp-dir build/tmp\n"
        "  python artifact_manager.py --sync-gitattributes"
    )
    parser = argparse.ArgumentParser(
        description="Manage packaging and recovery of session artifacts",
        epilog=examples,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help=(
            "create a session archive from files in the temporary directory "
            "(default: %(default)s). Example: --package --tmp-dir build/tmp"
        ),
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help=(
            "restore the most recent session archive back into the temporary "
            "directory (default: %(default)s). Example: --recover"
        ),
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help=(
            "commit the created archive to git (default: %(default)s). "
            "Example: --package --commit"
        ),
    )
    parser.add_argument(
        "--message",
        help=(
            "commit message when packaging (default: timestamped message). "
            "Example: --message 'Add session artifacts'"
        ),
    )
    parser.add_argument(
        "--tmp-dir",
        default="tmp",
        help=(
            "working directory for session files; created if it does not exist "
            "(default: %(default)s). Example: --tmp-dir build/tmp"
        ),
    )
    parser.add_argument(
        "--sync-gitattributes",
        action="store_true",
        help=(
            "regenerate .gitattributes from policy and exit (default: %(default)s). "
            "Example: --sync-gitattributes"
        ),
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    repo_root = Path(__file__).resolve().parent
    tmp_dir = Path(args.tmp_dir)
    if not check_directory_health(tmp_dir, repo_root):
        sys.exit(1)

    policy = LfsPolicy(repo_root)

    if args.sync_gitattributes:
        logger.info("Synchronizing .gitattributes")
        try:
            policy.sync_gitattributes()
            subprocess.run(
                ["git", "add", ".gitattributes"],
                cwd=repo_root,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:  # noqa: BLE001
            msg = exc.stderr.decode().strip() if exc.stderr else str(exc)
            logger.error("Git command failed: %s", msg)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            logger.error("sync_gitattributes failed: %s", exc)
            sys.exit(1)
        else:
            logger.info(".gitattributes synchronized")
        return

    if args.package:
        try:
            package_session(
                tmp_dir,
                repo_root,
                policy,
                commit=args.commit,
                message=args.message,
            )
        except FileNotFoundError as exc:
            logger.error("Temporary directory not found: %s", exc)
            sys.exit(1)
        except subprocess.CalledProcessError as exc:  # noqa: BLE001
            msg = exc.stderr.decode().strip() if exc.stderr else str(exc)
            logger.error("Git command failed during packaging: %s", msg)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            logger.error("Packaging failed: %s", exc)
            sys.exit(1)

    if args.recover:
        recover_latest_session(tmp_dir, repo_root, policy)


if __name__ == "__main__":
    main()
