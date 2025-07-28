"""Validation utilities for gh_COPILOT Enterprise Toolkit"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from utils.cross_platform_paths import CrossPlatformPathManager


def validate_workspace_integrity() -> Dict[str, Any]:
    """Validate workspace integrity and structure"""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))

    validation_results = {
        "workspace_exists": workspace.exists(),
        "required_directories": {},
        "forbidden_patterns": [],
        "overall_status": "UNKNOWN"
    }

    # Check required directories
    required_dirs = ["databases", "scripts", "utils", "documentation"]
    for dir_name in required_dirs:
        dir_path = workspace / dir_name
        validation_results["required_directories"][dir_name] = dir_path.exists()

    # Check for forbidden patterns (anti-recursion)
    forbidden = ["backup", "temp", "copy"]
    for pattern in forbidden:
        if pattern in str(workspace).lower():
            validation_results["forbidden_patterns"].append(pattern)

    # Determine overall status
    if (validation_results["workspace_exists"] and
        all(validation_results["required_directories"].values()) and
            not validation_results["forbidden_patterns"]):
        validation_results["overall_status"] = "VALID"
    else:
        validation_results["overall_status"] = "INVALID"

    return validation_results


def validate_script_organization() -> Dict[str, Any]:
    """Validate script organization structure"""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    scripts_dir = workspace / "scripts"

    organization_status = {
        "scripts_directory_exists": scripts_dir.exists(),
        "categories": {},
        "root_python_files": 0,
        "organized_python_files": 0,
        "organization_percentage": 0.0
    }

    if scripts_dir.exists():
        # Count organized scripts
        for category_dir in scripts_dir.iterdir():
            if category_dir.is_dir():
                py_files = list(category_dir.glob("*.py"))
                organization_status["categories"][category_dir.name] = len(py_files)
                organization_status["organized_python_files"] += len(py_files)

    # Count root Python files
    root_py_files = list(workspace.glob("*.py"))
    organization_status["root_python_files"] = len(root_py_files)

    # Calculate organization percentage
    total_scripts = organization_status["organized_python_files"] + \
        organization_status["root_python_files"]
    if total_scripts > 0:
        organization_status["organization_percentage"] = (
            organization_status["organized_python_files"] / total_scripts * 100
        )

    return organization_status


def detect_zero_byte_files(target_dir: Path) -> List[Path]:
    """Return a list of zero-byte files under ``target_dir``."""
    target = Path(target_dir)
    return [f for f in target.rglob("*") if f.is_file() and f.stat().st_size == 0]


def validate_path(path: Path) -> bool:
    """Return True if ``path`` is within workspace and not inside backup."""
    workspace = CrossPlatformPathManager.get_workspace_path().resolve()
    backup_root = CrossPlatformPathManager.get_backup_root().resolve()
    try:
        resolved = path.resolve()
    except FileNotFoundError:
        return False
    return workspace in resolved.parents and backup_root not in resolved.parents


def validate_enterprise_environment() -> bool:
    """Ensure workspace and backup paths are set and non-recursive."""
    workspace = CrossPlatformPathManager.get_workspace_path().resolve()
    backup_root_env = os.getenv("GH_COPILOT_BACKUP_ROOT")
    if not backup_root_env:
        raise EnvironmentError("GH_COPILOT_BACKUP_ROOT is not set")
    backup_root = Path(backup_root_env).resolve()

    if not workspace.exists():
        raise EnvironmentError("GH_COPILOT_WORKSPACE does not exist")

    if backup_root.exists() and workspace in backup_root.parents:
        raise EnvironmentError("Backup root must be outside the workspace")

    if not backup_root.parent.exists():
        raise EnvironmentError("Backup root parent directory is missing")

    return True


def operations_validate_workspace() -> None:
    """Run comprehensive workspace checks and print a JSON report."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    integrity = validate_workspace_integrity()
    organization = validate_script_organization()
    zero_bytes = [str(p) for p in detect_zero_byte_files(workspace)]
    report = {
        "integrity": integrity,
        "organization": organization,
        "zero_byte_files": zero_bytes,
    }
    print(json.dumps(report, indent=2))
