#!/usr/bin/env python3
"""Generate a Next Session Prompt.

This script parses the latest session validation report and the
`NEXT_SESSION_ENTROPY_RESOLUTION.md` document to create a short summary
of unresolved tasks for the next Copilot session.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
<<<<<<< HEAD
from secondary_copilot_validator import SecondaryCopilotValidator
from typing import List, Tuple
=======
from typing import List, Tuple
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def _latest_report(directory: Path) -> Path | None:
    reports = sorted(directory.glob("session_validation_report_*.json"))
    return reports[-1] if reports else None


def _parse_report(report_path: Path) -> Tuple[str, List[str]]:
    data = json.loads(report_path.read_text())
    status = data.get("overall_status", "UNKNOWN")
    failures = []
    if status != "COMPLETED":
        results = data.get("validation_results", {})
        failures = [name for name, ok in results.items() if not ok]
    return status, failures


def _parse_entropy(entropy_path: Path) -> List[str]:
    tasks: List[str] = []
    content = entropy_path.read_text().splitlines()
    capture = False
    for line in content:
        if line.strip().startswith("PRIORITY"):
            capture = True
            continue
        if capture:
            if line.strip().startswith("-"):
                tasks.append(re.sub(r"^-\s*", "", line).strip())
            elif line.strip() == "":
                continue
            elif not line.startswith(" ") and not line.startswith("-"):
                break
    return tasks


def generate_next_session_prompt(directory: Path | None = None) -> str:
    directory = directory or Path.cwd()
    report = _latest_report(directory)
    entropy_file = directory / "NEXT_SESSION_ENTROPY_RESOLUTION.md"
    tasks = _parse_entropy(entropy_file) if entropy_file.exists() else []
    status = "MISSING"
    failures: List[str] = []
    if report and report.exists():
        status, failures = _parse_report(report)
    prompt_lines = ["Next Session Prompt:"]
    if status != "COMPLETED":
        prompt_lines.append(f"Validation Status: {status}")
    if failures:
        prompt_lines.append("Outstanding Checks: " + ", ".join(failures))
    if tasks:
        prompt_lines.append("Key Tasks:")
        for task in tasks:
            prompt_lines.append(f"- {task}")
<<<<<<< HEAD
    prompt = "\n".join(prompt_lines)
    files = []
    if report and report.exists():
        files.append(str(report))
    if entropy_file.exists():
        files.append(str(entropy_file))
    if files:
        SecondaryCopilotValidator().validate_corrections(files)
    return prompt
=======
    return "\n".join(prompt_lines)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def main() -> None:
    prompt = generate_next_session_prompt()
    print(prompt)


if __name__ == "__main__":
    main()
