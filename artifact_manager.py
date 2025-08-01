"""Utility for packaging and recovering session artifacts.

The design intentionally mirrors real‑world backup tooling where artifacts
generated during a development session are archived for later inspection or
disaster recovery.  The archive destination is driven by the
``session_artifact_dir`` key in ``.codex_lfs_policy.yaml``.  When that file is
missing or the key is invalid, a safe default of ``"codex_sessions"`` is used.

Key principles implemented in this module:

* **Robust configuration parsing** – malformed YAML, permission errors or bad
  types are handled gracefully with clear log messages.
* **Configurable directories** – the active artifact directory is exposed via
  :attr:`ArtifactManager.session_artifact_dir` so no paths are hard coded.
* **Atomic writes** – archives are written to a temporary file and only moved to
  their final location after a successful write to avoid partial data on crash.
* **Cross‑platform compatibility** – path validation and directory creation use
  ``pathlib``/``os`` primitives that work on Linux, macOS and Windows.

The module exposes a small :class:`ArtifactManager` class with high level
``package_session`` and ``recover_latest_session`` helpers as well as a simple
command line interface for direct use.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from zipfile import ZipFile

import yaml
from yaml import YAMLError


logger = logging.getLogger(__name__)


class LfsPolicy:
    """Configuration for Git LFS compliance.

    Parameters read from ``.codex_lfs_policy.yaml`` include:

    - ``enable_autolfs``: toggle automatic ``git lfs track``.
    - ``size_threshold_mb``: file size threshold for automatic LFS.
    - ``binary_extensions``: extensions always placed in LFS.
    - ``gitattributes_template``: base template for ``.gitattributes``.
    - ``session_artifact_dir``: directory for storing session archives.
    """

    def __init__(self, root: Path) -> None:
        """Parse ``.codex_lfs_policy.yaml`` for LFS and session settings.

        Parameters
        ----------
        root:
            Repository root used to locate the policy file.  The constructor is
            intentionally forgiving so callers can rely on sane defaults even
            when the policy file is missing or malformed.
        """

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
        self.session_artifact_dir = "codex_sessions"
        self.root = root
        self._raw: dict[str, object] = {}

        policy_file = root / ".codex_lfs_policy.yaml"
        logger.debug("Reading policy from %s", policy_file)
        if policy_file.exists():
            try:
                self._raw = yaml.safe_load(policy_file.read_text()) or {}
            except YAMLError as exc:  # malformed YAML
                logger.error("Malformed YAML in %s: %s", policy_file, exc)
            except OSError as exc:  # permission or IO error
                logger.error("Unable to read %s: %s", policy_file, exc)
            else:
                logger.info("Loaded LFS policy from %s", policy_file)
        else:
            logger.info("%s not found", policy_file)
            logger.info("Using default LFS policy values")

        data = self._raw
        self.enabled = bool(data.get("enable_autolfs", False))
        self.size_threshold_mb = int(data.get("size_threshold_mb", 50))
        self.binary_extensions = list(data.get("binary_extensions", self.binary_extensions))
        self.gitattributes_template = data.get("gitattributes_template", "")

        session_dir = data.get("session_artifact_dir", self.session_artifact_dir)
        if not isinstance(session_dir, str) or not session_dir.strip():
            logger.warning(
                "Invalid session_artifact_dir %r; using default %s",
                session_dir,
                self.session_artifact_dir,
            )
        else:
            self.session_artifact_dir = session_dir.rstrip("/")

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
            subprocess.run(
                ["git", "lfs", "install"],
                cwd=self.root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "lfs", "track", path.name],
                cwd=self.root,
                check=True,
                capture_output=True,
            )
            git_attr = self.root / ".gitattributes"
            if git_attr.exists():
                subprocess.run(
                    ["git", "add", git_attr.name],
                    cwd=self.root,
                    check=True,
                    capture_output=True,
                )
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

        content = (
            "# Git LFS rules for binary artifacts\n"
            + "\n".join(lines)
            + "\n# End of LFS patterns\n"
        )

        current = attrs_file.read_text(encoding="utf-8") if attrs_file.exists() else ""
        if current.strip() != content.strip():
            attrs_file.write_text(content, encoding="utf-8")
            logger.info("Updated %s", attrs_file)


def _check_dir_health(path: Path, *, allow_symlink: bool = False) -> None:
    """Ensure ``path`` exists, is writable and safe.

    The check avoids common pitfalls such as using a symlinked directory that
    might escape the repository.  It raises :class:`RuntimeError` on failure so
    callers can handle it explicitly.
    """

    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:  # noqa: BLE001
        raise RuntimeError(f"Unable to create {path}: {exc}") from exc

    if path.is_symlink() and not allow_symlink:
        raise RuntimeError(f"Artifact directory {path} must not be a symlink")

    try:
        test_file = path / ".write_test"
        with test_file.open("w", encoding="utf-8"):
            pass
        test_file.unlink()
    except OSError as exc:  # noqa: BLE001
        raise RuntimeError(f"Artifact directory {path} not writable: {exc}") from exc


def detect_tmp_changes(tmp_dir: Path, repo_root: Path) -> List[Path]:
    """Return all files under ``tmp_dir`` relative to ``repo_root``."""

    if not tmp_dir.exists():
        logger.info("Temporary directory %s does not exist.", tmp_dir)
        return []

    return [p for p in tmp_dir.rglob("*") if p.is_file()]


def create_zip(archive_path: Path, files: Iterable[Path], base_dir: Path) -> None:
    """Create ``archive_path`` containing ``files`` relative to ``base_dir``."""

    with ZipFile(archive_path, "w") as zf:
        for file in files:
            if file.exists():
                zf.write(file, arcname=file.relative_to(base_dir))


class ArtifactManager:
    """Manage packaging and recovery of session artifacts.

    Parameters
    ----------
    repo_root:
        Root directory of the repository.
    tmp_dir:
        Directory where temporary session files live.  Defaults to ``tmp``.
    policy:
        Optional :class:`LfsPolicy`.  When omitted a new instance is created.

    Notes
    -----
    The resolved artifact directory is exposed via
    :attr:`session_artifact_dir`.  The attribute is always a sub path of
    ``repo_root`` to avoid accidentally writing outside the repository.
    """

    def __init__(
        self, repo_root: Path, tmp_dir: Path | str = "tmp", policy: LfsPolicy | None = None
    ) -> None:
        self.repo_root = Path(repo_root)
        self.tmp_dir = Path(tmp_dir)
        self.policy = policy or LfsPolicy(self.repo_root)
        self.session_artifact_dir = self.repo_root / self.policy.session_artifact_dir
        _check_dir_health(self.session_artifact_dir)

    # ------------------------------------------------------------------
    def package_session(
        self, *, commit: bool = False, message: str | None = None
    ) -> Optional[Path]:
        """Package changed files in :attr:`tmp_dir` into an archive."""

        changed_files = detect_tmp_changes(self.tmp_dir, self.repo_root)
        if not changed_files:
            logger.info("No session artifacts detected in %s", self.tmp_dir)
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"codex-session_{timestamp}.zip"
        archive_path = self.session_artifact_dir / archive_name

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".tmp", dir=self.session_artifact_dir, delete=False
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
            create_zip(tmp_path, changed_files, self.tmp_dir)
            os.replace(tmp_path, archive_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to create archive: %s", exc)
            if "tmp_path" in locals():
                try:
                    tmp_path.unlink()
                except FileNotFoundError:
                    pass
            return None
        finally:
            # remove stray temp files from previous failed writes
            for tmp in self.session_artifact_dir.glob("*.tmp"):
                try:
                    tmp.unlink()
                except OSError:
                    pass

        for file in changed_files:
            try:
                file.unlink()
            except FileNotFoundError:
                continue
            parent = file.parent
            while parent != self.tmp_dir and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

        logger.info("Created session archive %s", archive_path)

        if self.policy and self.policy.requires_lfs(archive_path):
            self.policy.track(archive_path)

        if commit:
            try:
                subprocess.run(
                    ["git", "add", str(archive_path.relative_to(self.repo_root))],
                    cwd=self.repo_root,
                    check=True,
                )
                try:
                    tracked = subprocess.check_output(
                        [
                            "git",
                            "lfs",
                            "ls-files",
                            str(archive_path.relative_to(self.repo_root)),
                        ],
                        cwd=self.repo_root,
                        text=True,
                    )
                except subprocess.CalledProcessError:
                    tracked = ""
                if self.policy.enabled and not tracked.strip():
                    logger.error("Archive %s is not tracked by Git LFS", archive_path)
                commit_msg = message or f"Add session artifact {timestamp}"
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=self.repo_root,
                    check=True,
                )
                logger.info("Committed archive %s", archive_path)
            except subprocess.CalledProcessError as exc:  # noqa: BLE001
                logger.error("Failed to commit archive: %s", exc)

        return archive_path

    # ------------------------------------------------------------------
    def recover_latest_session(self) -> Optional[Path]:
        """Restore files from the most recent session archive."""

        if not self.session_artifact_dir.exists():
            logger.warning("%s does not exist", self.session_artifact_dir)
            return None

        archives = sorted(
            self.session_artifact_dir.glob("codex-session_*.zip"), reverse=True
        )
        if not archives:
            logger.warning(
                "No session archives found in %s", self.session_artifact_dir
            )
            return None

        archive = archives[0]
        try:
            with ZipFile(archive) as zf:
                zf.extractall(self.tmp_dir)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to extract %s: %s", archive, exc)
            return None

        logger.info("Recovered session from %s", archive)
        return archive


# Backwards compatible functional wrappers -------------------------------
def package_session(
    tmp_dir: Path,
    repo_root: Path,
    lfs_policy: Optional[LfsPolicy] = None,
    *,
    commit: bool = False,
    message: str | None = None,
) -> Optional[Path]:
    manager = ArtifactManager(repo_root, tmp_dir, lfs_policy)
    return manager.package_session(commit=commit, message=message)


def recover_latest_session(
    tmp_dir: Path, repo_root: Path, lfs_policy: Optional[LfsPolicy] = None
) -> Optional[Path]:
    manager = ArtifactManager(repo_root, tmp_dir, lfs_policy)
    return manager.recover_latest_session()


def main() -> None:
    """Command-line interface for session packaging and recovery.

    The CLI is intentionally compact while offering sensible defaults.  Example
    usages::

        python artifact_manager.py --package --commit
        python artifact_manager.py --recover
        python artifact_manager.py --package --tmp-dir build/tmp
        python artifact_manager.py --sync-gitattributes
    """

    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Examples:\n  python %(prog)s --package --commit\n  python %(prog)s --recover",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Package files from the temporary directory into a zip archive",
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Restore the latest session archive into the temporary directory",
    )
    parser.add_argument(
        "--commit", action="store_true", help="Commit the created archive to git"
    )
    parser.add_argument("--message", help="Commit message when packaging")
    parser.add_argument(
        "--tmp-dir",
        default="tmp",
        help="Temporary directory containing session outputs (default: %(default)s)",
    )
    parser.add_argument(
        "--sync-gitattributes",
        action="store_true",
        help="Regenerate .gitattributes from policy before other actions",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    repo_root = Path(__file__).resolve().parent
    manager = ArtifactManager(repo_root, Path(args.tmp_dir))

    if args.sync_gitattributes:
        logger.info("Synchronizing .gitattributes")
        try:
            manager.policy.sync_gitattributes()
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to synchronize .gitattributes: %s", exc)

    if args.package:
        manager.package_session(commit=args.commit, message=args.message)

    if args.recover:
        manager.recover_latest_session()


if __name__ == "__main__":
    main()
