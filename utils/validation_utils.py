"""Validation utilities for gh_COPILOT Enterprise Toolkit"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Callable
from functools import wraps
import tempfile
import os
import psutil

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.lessons_learned_integrator import store_lesson


def calculate_composite_compliance_score(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders: int,
) -> Dict[str, float]:
    """Return detailed compliance scores for dashboard display.

    Parameters
    ----------
    ruff_issues: int
        Total number of lint issues reported by Ruff.
    tests_passed: int
        Number of tests that passed.
    tests_failed: int
        Number of tests that failed.
    placeholders: int
        Remaining placeholder markers in the repository.

    Returns
    -------
    Dict[str, float]
        Dictionary containing ``lint_score``, ``test_score``,
        ``placeholder_score`` and ``composite``. The composite score is
        weighted at 40% lint, 40% tests, and 20% placeholders.
    """

    total_tests = tests_passed + tests_failed
    test_score = (tests_passed / total_tests * 100) if total_tests else 0.0
    lint_score = max(0.0, 100 - ruff_issues)
    placeholder_score = max(0.0, 100 - (10 * placeholders))
    composite = round(
        0.4 * lint_score + 0.4 * test_score + 0.2 * placeholder_score,
        2,
    )
    return {
        "lint_score": round(lint_score, 2),
        "test_score": round(test_score, 2),
        "placeholder_score": round(placeholder_score, 2),
        "composite": composite,
    }


def validate_workspace_integrity() -> Dict[str, Any]:
    """Validate workspace integrity and structure"""
    workspace = CrossPlatformPathManager.get_workspace_path()

    validation_results = {
        "workspace_exists": workspace.exists(),
        "required_directories": {},
        "forbidden_patterns": [],
        "overall_status": "UNKNOWN",
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
    if (
        validation_results["workspace_exists"]
        and all(validation_results["required_directories"].values())
        and not validation_results["forbidden_patterns"]
    ):
        validation_results["overall_status"] = "VALID"
    else:
        validation_results["overall_status"] = "INVALID"

    return validation_results


def validate_script_organization() -> Dict[str, Any]:
    """Validate script organization structure"""
    workspace = CrossPlatformPathManager.get_workspace_path()
    scripts_dir = workspace / "scripts"

    organization_status = {
        "scripts_directory_exists": scripts_dir.exists(),
        "categories": {},
        "root_python_files": 0,
        "organized_python_files": 0,
        "organization_percentage": 0.0,
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
    total_scripts = organization_status["organized_python_files"] + organization_status["root_python_files"]
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
    backup_root = CrossPlatformPathManager.get_backup_root().resolve()

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


def run_compliance_gates(
    gates: Iterable[Tuple[str, bool]], *, db_path: Path | None = None
) -> bool:
    """Execute compliance gates and record failed checks as lessons.

    Parameters
    ----------
    gates:
        Iterable of (name, passed) pairs.
    db_path:
        Optional path for the lessons database.

    Returns
    -------
    bool
        ``True`` if all gates passed, ``False`` otherwise.
    """

    all_passed = True
    timestamp = datetime.utcnow().isoformat()
    for name, passed in gates:
        if not passed:
            all_passed = False
            kwargs = {}
            if db_path is not None:
                kwargs["db_path"] = db_path
            store_lesson(
                description=f"Compliance gate failed: {name}",
                source="compliance_gate",
                timestamp=timestamp,
                validation_status="pending",
                tags="compliance",
                **kwargs,
            )
    return all_passed


_LOCK_DIR = Path(tempfile.gettempdir()) / "gh_copilot_locks"
_LOCK_DIR.mkdir(exist_ok=True)


def anti_recursion_guard(func: Callable) -> Callable:
    """Decorator preventing recursive invocation using lock and PID files."""

    lock_file = _LOCK_DIR / f"{func.__name__}.lock"
    pid_file = _LOCK_DIR / f"{func.__name__}.pid"

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_pid = os.getpid()
        if lock_file.exists():
            raise RuntimeError("Anti-recursion guard triggered")
        if pid_file.exists():
            try:
                existing = int(pid_file.read_text().strip())
            except ValueError:
                existing = None
            if existing and psutil.pid_exists(existing):
                raise RuntimeError("PID guard triggered")
        try:
            lock_file.touch()
            pid_file.write_text(str(current_pid))
            return func(*args, **kwargs)
        finally:
            lock_file.unlink(missing_ok=True)
            try:
                if pid_file.exists() and int(pid_file.read_text().strip()) == current_pid:
                    pid_file.unlink()
            except Exception:  # pragma: no cover - best effort cleanup
                pid_file.unlink(missing_ok=True)

    return wrapper


def run_dual_copilot_validation(primary: Callable[[], bool], secondary: Callable[[], bool]) -> bool:
    """Run primary and secondary validators with explicit failure reporting.

    Both validators are executed even if the primary raises an exception.
    Any exceptions are captured and reported after both validators run. If
    either validator raises an exception, a ``RuntimeError`` describing the
    failure(s) is raised. Otherwise, the combined boolean result of both
    validators is returned.
    """

    errors: list[str] = []

    try:
        primary_result = bool(primary())
    except Exception as exc:  # pragma: no cover - defensive
        primary_result = False
        errors.append(f"Primary validation error: {exc}")

    try:
        secondary_result = bool(secondary())
    except Exception as exc:  # pragma: no cover - defensive
        secondary_result = False
        errors.append(f"Secondary validation error: {exc}")

    if errors:
        raise RuntimeError("; ".join(errors))

    return primary_result and secondary_result
