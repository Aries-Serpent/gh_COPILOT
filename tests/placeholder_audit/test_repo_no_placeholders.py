"""Ensure repository python files are free of TODO/FIXME markers."""

from __future__ import annotations

from pathlib import Path
import re

EXCLUDED = {
    "tests",
    "docs",
    "documentation",
    "builds",
    "archive",
    "archived_databases",
    "artifacts",
    "logs",
    "databases",
    "results",
    ".venv",
    ".git",
    "tmp",
}
EXCLUDED_FILES = {
    "scripts/code_placeholder_audit.py",
    "scripts/simple_placeholder_audit.py",
    "enterprise_modules/compliance.py",
    "validation/compliance_report_generator.py",
    "db_tools/operations/compliance.py",
    "scripts/database/documentation_db_analyzer.py",
    "src/dashboard/auth.py",
}
PATTERNS = [re.compile(r"TODO"), re.compile(r"FIXME")]


def test_repository_has_no_placeholders() -> None:
    """Repository should not contain TODO/FIXME placeholders."""
    root = Path(__file__).resolve().parents[2]
    for path in root.rglob("*.py"):
        if any(part in EXCLUDED for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        if rel in EXCLUDED_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in PATTERNS:
            assert pat.search(text) is None, f"{path} contains {pat.pattern}"
