#!/usr/bin/env python3
"""Validate that script paths referenced in documentation exist."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

DOC_EXTENSIONS = {".md", ".rst"}
SCRIPT_PATTERN = re.compile(r"scripts/database/[\w./-]+\.py")


def find_doc_files(root: Path) -> Iterable[Path]:
    # include root README files
    for name in ("README.md", "README.rst"):
        doc_path = root / name
        if doc_path.is_file():
            yield doc_path

    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for path in docs_dir.rglob("*"):
            if path.suffix in DOC_EXTENSIONS and path.is_file():
                yield path


def find_missing_script_refs(root: Path) -> List[Tuple[Path, str]]:
    missing: List[Tuple[Path, str]] = []
    for doc in find_doc_files(root):
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for match in SCRIPT_PATTERN.findall(text):
            script_path = root / match
            if not script_path.is_file():
                missing.append((doc, match))
    return missing


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    missing = find_missing_script_refs(repo_root)
    if missing:
        for doc, script in missing:
            print(f"{doc}: missing script '{script}'")
        return 1
    print("All referenced script paths exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
