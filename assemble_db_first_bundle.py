"""Assemble the DB-first bundle into a directory and zip archive.

This script recreates a minimal DB-first scaffold by copying selected
repository files into a fresh ``db_first_bundle`` folder and then
compressing that folder into ``db_first_bundle.zip``.  It mirrors the
behavior of the original one-shot assembler while using relative paths
instead of hard-coded locations.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
BUNDLE_DIR = ROOT / "db_first_bundle"
ZIP_PATH = ROOT / "db_first_bundle.zip"

# Paths relative to the repository root to include in the bundle.
INCLUDE = [
    "scripts",
    "src",
    "tests",
    "docs",
    ".github",
    ".gitattributes",
    ".pre-commit-config.yaml",
    "Makefile",
    "Taskfile.yml",
    "Makefile.win",
    "Invoke-DbFirst.ps1",
]


def clean_bundle() -> None:
    """Remove any existing bundle directory or zip file."""
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()


def copy_items() -> int:
    """Copy selected items into the bundle directory.

    Returns the number of files copied.
    """
    files = 0
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    for rel in INCLUDE:
        src = ROOT / rel
        dest = BUNDLE_DIR / rel
        if src.is_dir():
            shutil.copytree(src, dest)
            files += sum(1 for _ in dest.rglob("*") if _.is_file())
        elif src.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            files += 1
    return files


def create_zip() -> None:
    """Create a zip archive from the bundle directory."""
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in BUNDLE_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(BUNDLE_DIR))


def main() -> None:
    clean_bundle()
    files = copy_items()
    create_zip()
    print(json.dumps({"zip": str(ZIP_PATH), "files": files}, indent=2))


if __name__ == "__main__":
    main()
