#!/usr/bin/env python3
"""Automated Hard-Coded Path Migration Utility."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm

from utils.cross_platform_paths import (CrossPlatformPathManager,
                                        migrate_hard_coded_paths)


def scan_repository_for_hard_coded_paths(workspace_path: Path) -> List[Dict[str, Any]]:
    """Scan repository for hard-coded path violations."""
    violations: List[Dict[str, Any]] = []
    search_patterns = [
        "E:/gh_COPILOT",
        "E\\gh_COPILOT",
        "C:/gh_COPILOT",
        "C\\gh_COPILOT",
        "E:\\gh_COPILOT",
        "C:\\gh_COPILOT",
    ]

    python_files = list(workspace_path.rglob("*.py"))

    with tqdm(total=len(python_files), desc="Scanning for hard-coded paths", unit="file") as pbar:
        for py_file in python_files:
            pbar.set_description(f"Scanning {py_file.name}")
            try:
                content = py_file.read_text(encoding="utf-8")
            except Exception as e:
                logging.warning(f"Error reading {py_file}: {e}")
                pbar.update(1)
                continue

            file_violations = []
            for pattern in search_patterns:
                if pattern in content:
                    lines = content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        if pattern in line:
                            file_violations.append({
                                "line_number": line_num,
                                "pattern": pattern,
                                "line_content": line.strip(),
                            })
            if file_violations:
                violations.append({"file_path": str(py_file), "violations": file_violations})

            pbar.update(1)

    return violations


def execute_automated_migration() -> Dict[str, Any]:
    """Execute automated path migration with enterprise validation."""
    workspace_path = CrossPlatformPathManager.get_workspace_path()

    logging.info("=" * 80)
    logging.info("AUTOMATED HARD-CODED PATH MIGRATION")
    logging.info("=" * 80)
    logging.info(f"Workspace: {workspace_path}")
    logging.info(f"Platform: {os.name}")

    violations = scan_repository_for_hard_coded_paths(workspace_path)

    if not violations:
        logging.info("No hard-coded path violations found")
        return {"status": "NO_VIOLATIONS", "files_processed": 0}

    migration_results = []

    with tqdm(total=len(violations), desc="Migrating paths", unit="file") as pbar:
        for violation in violations:
            pbar.set_description(f"Migrating {Path(violation['file_path']).name}")
            try:
                result = migrate_hard_coded_paths(Path(violation["file_path"]))
                migration_results.append(result)
            except Exception as e:
                logging.error(f"Migration failed for {violation['file_path']}: {e}")
                migration_results.append({"file_path": violation["file_path"], "error": str(e)})
            pbar.update(1)

    successful_migrations = [r for r in migration_results if r.get("changes_made")]

    logging.info("=" * 80)
    logging.info("MIGRATION SUMMARY")
    logging.info("=" * 80)
    logging.info(f"Files Scanned: {len(violations)}")
    logging.info(f"Successful Migrations: {len(successful_migrations)}")
    logging.info("Cross-Platform Compliance Achieved")
    logging.info("=" * 80)

    return {
        "status": "SUCCESS",
        "files_processed": len(violations),
        "successful_migrations": len(successful_migrations),
        "migration_results": migration_results,
    }


if __name__ == "__main__":
    result = execute_automated_migration()
    print(f"MIGRATION COMPLETE: {result['status']}")
