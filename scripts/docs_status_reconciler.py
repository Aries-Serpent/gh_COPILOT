import argparse
import json
from pathlib import Path

import jsonschema

SCHEMA_PATH = Path(__file__).parent / "schemas" / "status_index.schema.json"
TASK_STUBS_PATH = Path("docs/task_stubs.md")
TASKS_STARTED_PATH = Path("docs/PHASE5_TASKS_STARTED.md")
STATUS_INDEX_PATH = Path("status_index.json")


def parse_task_stubs(path: Path) -> list[str]:
    tasks = []
    for line in path.read_text().splitlines():
        if line.startswith("| ") and "|" in line[2:]:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if parts and parts[0] not in ("Task", "---"):
                tasks.append(parts[0])
    return tasks


def parse_tasks_started(path: Path) -> list[str]:
    tasks = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            tasks.append(line[2:].strip())
    return tasks


def generate_status_index() -> dict[str, bool]:
    stubs = parse_task_stubs(TASK_STUBS_PATH)
    started = parse_tasks_started(TASKS_STARTED_PATH)
    unknown = sorted(set(started) - set(stubs))
    if unknown:
        raise ValueError(f"Unknown tasks in started list: {', '.join(unknown)}")
    return {task: task in started for task in stubs}


def validate_schema(data: dict[str, bool]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(data, schema)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile task status files")
    parser.add_argument("--check", action="store_true", help="exit non-zero on drift")
    args = parser.parse_args()

    try:
        index = generate_status_index()
        validate_schema(index)
    except Exception as exc:  # pragma: no cover - error path
        STATUS_INDEX_PATH.write_text(json.dumps({}, indent=2))
        print(exc)
        return 1

    if args.check:
        if STATUS_INDEX_PATH.exists():
            existing = json.loads(STATUS_INDEX_PATH.read_text())
            if existing == index:
                return 0
        STATUS_INDEX_PATH.write_text(json.dumps(index, indent=2))
        return 1

    STATUS_INDEX_PATH.write_text(json.dumps(index, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
