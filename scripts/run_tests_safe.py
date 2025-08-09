from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _has_pytest_cov() -> bool:
    """Check if pytest-cov plugin is available."""
    try:
        return importlib.util.find_spec("pytest_cov") is not None
    except ImportError:
        return False


def _has_json_report() -> bool:
    """Check if pytest-json-report plugin is available."""
    try:
        return importlib.util.find_spec("pytest_jsonreport") is not None
    except ImportError:
        return False


def run_pytest_safe(
    target_path: Optional[str] = None,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run pytest, attempting coverage and json report plugins if available.
    Always writes a test summary JSON to the output_file location.
    """
    args = []
    if target_path:
        args.append(target_path)
    cmd = ["pytest"]

    # Handle --json-report if available
    if _has_json_report():
        cmd.append("--json-report")
    
    # Handle coverage plugin
    if _has_pytest_cov():
        cmd.extend(["--cov=.", "--cov-report=term"])
    else:
        # Remove any --cov flags from PYTEST_ADDOPTS if present
        addopts = os.environ.get("PYTEST_ADDOPTS", "").split()
        addopts = [opt for opt in addopts if not opt.startswith("--cov")]
        os.environ["PYTEST_ADDOPTS"] = " ".join(addopts)
        if "-q" not in cmd:
            cmd.insert(1, "-q")

    cmd.extend(args)

    # Run the test command
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=300)
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "exit_code": -1,
            "error": "Test execution timed out after 300 seconds",
            "coverage_enabled": _has_pytest_cov(),
            "success": False,
        }

    # Compose the summary
    summary: Dict[str, Any] = {
        "command": " ".join(cmd),
        "returncode": returncode,
        "coverage_enabled": _has_pytest_cov(),
        "stdout_lines": len(proc.stdout.splitlines()) if proc.stdout else 0,
        "stderr_lines": len(proc.stderr.splitlines()) if proc.stderr else 0,
        "success": returncode == 0,
    }

    # Try to extract json-report summary if available
    report_json_path = Path(".report.json")
    if report_json_path.exists():
        try:
            data = json.loads(report_json_path.read_text(encoding="utf-8"))
            summary.update(data.get("summary", {}))
        except Exception:
            pass

    # Attempt to infer failures/passes/errors from text output as fallback
    stdout_lower = proc.stdout.lower() if proc.stdout else ""
    if "failed" in stdout_lower:
        summary["has_failures"] = True
    if "passed" in stdout_lower:
        summary["has_passes"] = True
    if "error" in stdout_lower:
        summary["has_errors"] = True

    # Output file path
    out_file = output_file or "artifacts/test_failures_summary.json"
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    # Save summary
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe pytest runner with coverage and JSON reporting support.")
    parser.add_argument("--target", default=None, help="Target path for tests (default: current directory)")
    parser.add_argument("--output", default="artifacts/test_failures_summary.json", help="Output file for summary JSON")
    args, unknown = parser.parse_known_args()
    # Allow passing extra pytest CLI args after "--"
    if unknown:
        sys.argv = sys.argv[:1] + unknown

    summary = run_pytest_safe(target_path=args.target, output_file=args.output)

    if summary.get("success"):
        return 0
    else:
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "_has_pytest_cov",
    "_has_json_report",
    "run_pytest_safe",
    "main",
]
