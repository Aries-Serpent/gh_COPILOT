"""Ensure core modules remain free of TODO/FIXME placeholders."""

from __future__ import annotations

from pathlib import Path
import re


FILES = [
    Path("database_first_synchronization_engine.py"),
    Path("template_engine/db_first_code_generator.py"),
    Path("validation/protocols/documentation_manager.py"),
    Path("scripts/database/cross_database_reconciler.py"),
    Path("template_engine/template_synchronizer.py"),
    Path("archive/consolidated_scripts/enterprise_database_driven_documentation_manager.py"),
]

PATTERNS = [r"TODO", r"FIXME", r"placeholder"]


def test_core_modules_have_no_placeholders() -> None:
    """Assert core modules do not contain placeholder markers."""
    for file in FILES:
        text = file.read_text(encoding="utf-8")
        for pattern in PATTERNS:
            assert re.search(pattern, text) is None, f"{file} contains {pattern}"

