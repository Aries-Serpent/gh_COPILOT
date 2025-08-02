#!/usr/bin/env python3
"""Relocate legacy scripts and update import references.

This utility moves top-level files into their recommended package
locations using ``git mv`` and updates Python import statements across
the repository to prevent broken references.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, Iterable

# Mapping of source paths to destination directories
FILE_MOVES: Dict[str, str] = {
    "advanced_qubo_optimization.py": "scripts/optimization/",
    "artifact_manager.py": "scripts/utilities/",
    "autonomous_database_health_optimizer.py": "scripts/automation/",
    "complete_template_generator.py": "scripts/utilities/",
    "performance_validation_complete.py": "scripts/validation/",
    "performance_validation_framework.py": "scripts/validation/",
    "physics_optimization_engine.py": "scripts/optimization/",
    "script_database_validator.py": "db_tools/",
    "secondary_copilot_validator.py": "scripts/validation/",
    "simplified_quantum_integration_orchestrator.py": "scripts/session/",
    "temp_db_check.py": "db_tools/",
    "template_auto_generation_complete.py": "scripts/automation/",
    "unified_database_management_system.py": "scripts/database/",
    "unified_disaster_recovery_system.py": "scripts/utilities/",
    "unified_disaster_recovery_system.pyi": "scripts/utilities/",
    "unified_legacy_cleanup_system.py": "scripts/automation/",
    "unified_monitoring_optimization_system.py": "scripts/monitoring/",
    "unified_script_generation_system.py": "scripts/utilities/",
    "unified_session_management_system.py": "scripts/utilities/",
    "unified_session_management_system.pyi": "scripts/utilities/",
    "web_gui_integration_system.py": "scripts/utilities/",
    "web_gui_integration_system.pyi": "scripts/utilities/",
    # logs/results relocation handled separately
}

IMPORT_PATTERN = re.compile(r"^(\s*(?:from|import)\s+)([\w\.]+)(.*)$", re.MULTILINE)


def _git_mv(src: Path, dest: Path) -> None:
    """Move ``src`` to ``dest`` using ``git mv``.

    ``dest``'s parent directory is created automatically.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src), str(dest)], check=True)


def _iter_python_files(base: Path) -> Iterable[Path]:
    """Yield Python source files under ``base``."""
    yield from base.rglob("*.py")
    yield from base.rglob("*.pyi")


def _update_imports(base: Path, old_module: str, new_module: str, *, git_stage: bool = True) -> None:
    """Update import statements from ``old_module`` to ``new_module``.

    ``base`` defines the repository root to search within. When
    ``git_stage`` is ``False`` the modified files are not staged with
    ``git add``. This allows dry runs and unit tests without touching the
    repository index.
    """
    for path in _iter_python_files(base):
        text = path.read_text()
        changed = False

        def repl(match: re.Match[str]) -> str:
            nonlocal changed
            prefix, module, suffix = match.groups()
            if module == old_module:
                changed = True
                return f"{prefix}{new_module}{suffix}"
            return match.group(0)

        new_text = IMPORT_PATTERN.sub(repl, text)
        if changed:
            path.write_text(new_text)
            if git_stage:
                subprocess.run(["git", "add", str(path)], check=True)


def migrate(base: Path | None = None) -> None:
    """Execute migration for all defined file moves."""
    base = base or Path.cwd()
    for src_name, dest_dir in FILE_MOVES.items():
        src = base / src_name
        if not src.exists():
            continue
        dest = base / dest_dir / src.name
        old_module = src.with_suffix("").as_posix().replace("/", ".")
        _git_mv(src, dest)
        new_module = dest.with_suffix("").as_posix().replace("/", ".")
        _update_imports(base, old_module, new_module)

    # Move logs/results folders if present
    for directory in ("logs", "results"):
        src_dir = base / directory
        if src_dir.exists():
            dest_dir = base / "artifacts" / directory
            dest_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", str(src_dir), str(dest_dir)], check=True)


if __name__ == "__main__":
    migrate()
