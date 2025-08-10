#!/usr/bin/env python3
"""Reconcile task status documentation.

This script treats ``docs/PHASE5_TASKS_STARTED.md`` as the single source of
truth (SSOT). It parses the task sections from that file and generates two
artifacts:

* ``docs/task_stubs.md`` – A concise markdown table of task names, statuses and
  progress percentages.
* ``status_index.json`` – A machine‑readable mapping of task names to their
  status and progress.

Running the script keeps derived documentation in sync with the canonical
source file. The CI workflow uses this script to detect drift.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "PHASE5_TASKS_STARTED.md"
TASK_STUBS_MD = ROOT / "docs" / "task_stubs.md"
STATUS_INDEX_JSON = ROOT / "status_index.json"


def parse_tasks(text: str) -> list[dict[str, str]]:
    """Extract task metadata from the source markdown."""

    tasks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            if ". " not in line:
                # Ignore headings without a numeric prefix.
                current = None
                continue
            if current:
                tasks.append(current)
            name = line.split(". ", 1)[1].strip()
            current = {"task": name}
        elif "**Status:**" in line and current is not None:
            status = line.split("**Status:**", 1)[1].strip()
            current["status"] = status
        elif "**Progress:**" in line and current is not None:
            match = re.search(r"Progress:\*\*\s*(\d+%)", line)
            if match:
                current["progress"] = match.group(1)
    if current:
        tasks.append(current)
    return tasks


def write_markdown(tasks: list[dict[str, str]]) -> None:
    """Write the aggregated markdown table."""

    with TASK_STUBS_MD.open("w", encoding="utf-8") as fh:
        fh.write("# Task Status Overview\n\n")
        fh.write("| Task | Status | Progress |\n| --- | --- | --- |\n")
        for task in tasks:
            fh.write(
                f"| {task['task']} | {task.get('status', '')} | {task.get('progress', '')} |\n"
            )


def write_json(tasks: list[dict[str, str]]) -> None:
    """Write the machine readable index."""

    index = {
        task["task"]: {
            "status": task.get("status", ""),
            "progress": task.get("progress", ""),
        }
        for task in tasks
    }
    with STATUS_INDEX_JSON.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    tasks = parse_tasks(text)
    write_markdown(tasks)
    write_json(tasks)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

