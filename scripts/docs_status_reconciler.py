#!/usr/bin/env python3
"""Generate documentation status indexes.

The script scans markdown files under ``docs/`` for YAML front matter containing
``id`` and ``status`` fields. It aggregates this metadata into two derived
artifacts:

* ``docs/task_stubs.md`` – human‑readable table linking each document to its
  status.
* ``docs/status_index.json`` – machine‑readable mapping of document ``id`` to
  status and source path.

Run this script before committing to keep these artifacts in sync. CI calls the
script and fails if the generated files differ from what is committed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
TASK_STUBS = DOCS_DIR / "task_stubs.md"
STATUS_INDEX = DOCS_DIR / "status_index.json"


def _parse_front_matter(path: Path) -> dict[str, str] | None:
    """Return front-matter metadata for ``path``.

    The function expects the file to start with a YAML front-matter block. Only
    entries containing both ``id`` and ``status`` keys are returned.
    """

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    try:
        _, fm, _ = text.split("---", 2)
    except ValueError:
        return None
    data = yaml.safe_load(fm) or {}
    if "id" in data and "status" in data:
        return {
            "id": str(data["id"]),
            "status": str(data["status"]),
            "file": path.relative_to(DOCS_DIR).as_posix(),
        }
    return None


def _collect_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for md in DOCS_DIR.glob("*.md"):
        meta = _parse_front_matter(md)
        if meta:
            entries.append(meta)
    return sorted(entries, key=lambda x: x["id"])


def _write_markdown(entries: Iterable[dict[str, str]]) -> None:
    with TASK_STUBS.open("w", encoding="utf-8") as fh:
        fh.write("# Task Status Overview\n\n")
        fh.write("| ID | Status | Document |\n| --- | --- | --- |\n")
        for entry in entries:
            fh.write(
                f"| {entry['id']} | {entry['status']} | [{entry['file']}]({entry['file']}) |\n"
            )


def _write_json(entries: Iterable[dict[str, str]]) -> None:
    index = {
        entry["id"]: {"status": entry["status"], "file": entry["file"]}
        for entry in entries
    }
    with STATUS_INDEX.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)


def main() -> None:  # pragma: no cover - CLI entry
    entries = _collect_entries()
    _write_markdown(entries)
    _write_json(entries)


if __name__ == "__main__":  # pragma: no cover
    main()

