#!/usr/bin/env python3
"""Validate security configuration files and export reports.

This script inspects JSON files stored under the repository's
``security`` directory. Each configuration is validated against a set of
critical rules. Missing critical keys cause the process to exit with a
non-zero status. Validation results are written to
``reports/security_validator.json`` and ``reports/security_validator.csv``.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

CONFIG_DIR = Path(__file__).resolve().parent

# Critical rules expected in each configuration file. Keys listed under
# ``critical`` must exist at the top level of the respective JSON file.
SEVERITY_RULES: Dict[str, Dict[str, Iterable[str]]] = {
    "access_control_matrix.json": {"critical": ["directory_permissions"]},
    "encryption_standards.json": {"critical": ["encryption_requirements"]},
    "enterprise_security_policy.json": {"critical": ["security_controls"]},
    "security_audit_framework.json": {"critical": ["audit_categories"]},
}


def load_security_configs(config_dir: Path) -> Dict[str, Any]:
    """Return parsed security configuration data from ``config_dir``."""

    configs: Dict[str, Any] = {}
    for path in config_dir.glob("*.json"):
        with path.open(encoding="utf-8") as handle:
            configs[path.name] = json.load(handle)
    return configs


def validate_security_configs(config_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Validate configuration files and report missing critical keys."""

    configs = load_security_configs(config_dir)
    results: Dict[str, Dict[str, Any]] = {}
    for name, data in configs.items():
        missing = [
            key
            for key in SEVERITY_RULES.get(name, {}).get("critical", [])
            if key not in data
        ]
        status = "fail" if missing else "pass"
        results[name] = {"status": status, "missing": missing}
    return results


def write_reports(results: Dict[str, Dict[str, Any]], report_dir: Path) -> None:
    """Write validation results to JSON and CSV files in ``report_dir``."""

    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "security_validator.json"
    csv_path = report_dir / "security_validator.csv"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "status", "missing"])
        for name, info in results.items():
            writer.writerow([name, info["status"], ";".join(info["missing"])])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()

    results = validate_security_configs(args.config_dir)
    write_reports(results, args.report_dir)

    has_failures = any(info["status"] == "fail" for info in results.values())
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
