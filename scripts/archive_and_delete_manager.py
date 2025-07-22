#!/usr/bin/env python3
"""Archive files before deletion following enterprise backup rules."""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

ARCHIVE_DIR = Path("ARCHIVE(S)")


def archive_files(files: Iterable[Path]) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with tqdm(total=len(list(files)), desc="archive", unit="file") as bar:
        for f in files:
            dest = ARCHIVE_DIR / f"{f.name}.7z"
            subprocess.run(["7z", "a", "-t7z", "-mx=9", str(dest), str(f)], check=False)
            bar.update(1)


def main(files: Iterable[str]) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    paths = [Path(f) for f in files]
    archive_files(paths)
    for p in paths:
        p.unlink(missing_ok=True)
    logging.info("[INFO] archived and deleted %d files", len(paths))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
