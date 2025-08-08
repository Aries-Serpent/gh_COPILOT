"""Utility functions for working with zip archives.

These helpers provide a small wrapper around :mod:`zipfile` that
includes a safety check to prevent path traversal when extracting
archives. The functions are intentionally lightweight so they can be
used in tests and simple scripts without additional dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import shutil
import zipfile


def _is_within_directory(base: Path, target: Path) -> bool:
    """Return ``True`` if *target* is located inside *base*.

    Both paths are resolved before comparison which protects against
    attempts to escape the destination directory using ``..`` segments
    or symbolic links.
    """

    try:
        base = base.resolve()
        target = target.resolve()
    except FileNotFoundError:
        # If the target does not exist yet we cannot resolve it; fall
        # back to joining the paths which is still safe because ``resolve``
        # was called on *base*.
        target = base.joinpath(target).resolve()

    return base == target or base in target.parents


def extract_zip(zip_path: Path | str, dest_dir: Path | str, *, overwrite: bool = False) -> List[Path]:
    """Extract ``zip_path`` into ``dest_dir`` safely.

    Parameters
    ----------
    zip_path:
        Path to the archive to extract.
    dest_dir:
        Directory where files should be written. The directory is created
        if it does not already exist.
    overwrite:
        If ``True`` existing files will be replaced. By default existing
        files are left untouched and skipped.

    Returns
    -------
    list[Path]
        The list of file paths that were extracted.

    Raises
    ------
    FileNotFoundError
        If ``zip_path`` does not exist.
    ValueError
        If an entry in the archive attempts path traversal outside of
        ``dest_dir``.
    """

    archive = Path(zip_path)
    if not archive.exists():
        raise FileNotFoundError(archive)

    destination = Path(dest_dir)
    destination.mkdir(parents=True, exist_ok=True)

    extracted: List[Path] = []
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            member_path = destination / member.filename
            if not _is_within_directory(destination, member_path):
                raise ValueError(f"unsafe path detected: {member.filename!r}")

            if member.is_dir():
                member_path.mkdir(parents=True, exist_ok=True)
                continue

            if member_path.exists() and not overwrite:
                continue

            member_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, member_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(member_path)

    return extracted


def create_zip(zip_path: Path | str, sources: Iterable[Path | str]) -> Path:
    """Create a zip archive at ``zip_path`` from ``sources``.

    Non-existent source paths are ignored. Directories are added
    recursively so their entire contents are included, and empty
    directories are preserved. The function returns the path to the
    created archive.
    """

    archive = Path(zip_path)
    archive.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "w") as zf:
        for src in sources:
            path = Path(src)
            if not path.exists():
                continue
            if path.is_dir():
                # Include the directory itself if it is empty so that
                # empty folders are preserved when the archive is
                # extracted later.
                if not any(path.iterdir()):
                    zf.writestr(path.name + "/", "")
                for item in path.rglob("*"):
                    if item.is_dir():
                        # ``ZipFile`` does not automatically create
                        # entries for empty directories, so we add
                        # them explicitly.
                        if not any(item.iterdir()):
                            zf.writestr(item.relative_to(path).as_posix() + "/", "")
                        continue
                    zf.write(item, arcname=item.relative_to(path))
                continue
            zf.write(path, arcname=path.name)

    return archive
