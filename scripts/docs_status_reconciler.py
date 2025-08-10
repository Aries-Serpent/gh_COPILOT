"""Reconcile Phase 5 task progress with task stubs.

This script parses ``docs/PHASE5_TASKS_STARTED.md`` and
``docs/task_stubs.md`` to ensure their progress values match.
It writes a JSON index of task progress and can be run in
``--check`` mode to fail when drift is detected.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import validate

PHASE5_PATH = Path("docs/PHASE5_TASKS_STARTED.md")
TASK_STUBS_PATH = Path("docs/task_stubs.md")
SCHEMA_PATH = Path("scripts/schemas/status_index.schema.json")
STATUS_INDEX_PATH = Path("status_index.json")


def _parse_phase5(path: Path) -> dict[str, int]:
    """Return mapping of task name to progress percentage."""
    tasks: dict[str, int] = {}
    current: str | None = None
    for line in path.read_text().splitlines():
        heading = re.match(r"^##\s+\d+\.\s+(.*)", line)
        if heading:
            current = heading.group(1).strip()
            continue
        if current:
            progress = re.search(r"Progress:\**\s*(\d+)%", line)
            if progress:
                tasks[current] = int(progress.group(1))
                current = None
    return tasks


def _parse_task_stubs(path: Path) -> dict[str, int]:
    """Return mapping from task stubs table."""
    tasks: dict[str, int] = {}
    lines = path.read_text().splitlines()
    for line in lines:
        if not line.startswith("|") or line.startswith("| Task "):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 7:
            continue
        name = parts[0]
        match = re.match(r"(\d+)%", parts[-1])
        if match:
            tasks[name] = int(match.group(1))
    return tasks


def reconcile(
    phase5_path: Path = PHASE5_PATH,
    stubs_path: Path = TASK_STUBS_PATH,
    *,
    schema_path: Path = SCHEMA_PATH,
    index_path: Path = STATUS_INDEX_PATH,
    check: bool = False,
) -> dict[str, dict[str, int]]:
    """Generate status index and optionally fail on drift.

    Returns a mapping of tasks with differing progress values.
    """
    phase5 = _parse_phase5(phase5_path)
    stubs = _parse_task_stubs(stubs_path)
    status_index = phase5

    schema = json.loads(schema_path.read_text())
    validate(status_index, schema)
    index_path.write_text(json.dumps(status_index, indent=2, sort_keys=True))

    drift: dict[str, dict[str, int]] = {}
    for task, pct in phase5.items():
        stub_pct = stubs.get(task)
        if stub_pct != pct:
            drift[task] = {"phase5": pct, "stubs": stub_pct or 0}
    if check and drift:
        raise SystemExit(1)
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail on drift")
    args = parser.parse_args(argv)
    try:
        reconcile(check=args.check)
    except SystemExit as exc:
        return exc.code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
