#!/usr/bin/env python3
"""Generate documentation status indexes.

The script parses ``docs/PHASE5_TASKS_STARTED.md`` for per‑task YAML front
matter blocks containing ``id`` and ``status`` fields. It aggregates this
metadata into two derived artifacts:

* ``docs/task_stubs.md`` – human‑readable table linking each task to its status.
* ``docs/status_index.json`` – machine‑readable mapping of task ``id`` to status
  and source anchor.

Run this script before committing to keep these artifacts in sync. CI calls the
script and fails if the generated files differ from what is committed.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Iterable
import logging

try:  # pragma: no cover - optional dependency
    import yaml
except ImportError:  # pragma: no cover - fallback for missing dependency
    yaml = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
TASK_STUBS = DOCS_DIR / "task_stubs.md"
STATUS_INDEX = DOCS_DIR / "status_index.json"
PHASE5_TASKS = DOCS_DIR / "PHASE5_TASKS_STARTED.md"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _collect_entries(path: Path = PHASE5_TASKS) -> list[dict[str, str]]:
    """Return task entries parsed from ``path``."""
    if yaml is None:
        logging.warning("PyYAML is not installed; skipping parsing for %s", path)
        return []

    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^###\s+(?P<title>.+?)\n---\n(?P<yaml>.+?)\n---", re.MULTILINE | re.DOTALL)
    entries: list[dict[str, str]] = []
    for match in pattern.finditer(text):
        title = match.group("title").strip()
        data = yaml.safe_load(match.group("yaml")) or {}
        if "id" in data and "status" in data:
            entries.append(
                {
                    "id": str(data["id"]),
                    "status": str(data["status"]),
                    "file": f"{path.name}#{_slug(title)}",
                }
            )
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

