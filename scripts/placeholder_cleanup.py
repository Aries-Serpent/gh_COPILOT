"""Placeholder Cleanup CLI.

This script orchestrates placeholder auditing, removal, logging, and dashboard
updates. It uses :mod:`scripts.code_placeholder_audit` for detection and
:mod:`template_engine.template_placeholder_remover` for cleanup.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
from scripts import code_placeholder_audit as audit


def main(
    workspace: Path,
    analytics_db: Path,
    production_db: Path,
    dashboard_dir: Path,
    timeout_minutes: int = 30,
) -> bool:
    patterns = audit.DEFAULT_PATTERNS + audit.fetch_db_placeholders(production_db)
    results = audit.scan_files(workspace, patterns, timeout_minutes * 60)
    audit.log_findings(results, analytics_db)
    audit.auto_remove_placeholders(results, production_db, analytics_db)
    audit.log_findings([], analytics_db, update_resolutions=True)
    ComplianceMetricsUpdater(dashboard_dir).update()
    return audit.validate_results(0, analytics_db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and clean placeholders")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("analytics_db", type=Path)
    parser.add_argument("production_db", type=Path)
    parser.add_argument("dashboard_dir", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    success = main(
        args.workspace,
        args.analytics_db,
        args.production_db,
        args.dashboard_dir,
        args.timeout,
    )
    raise SystemExit(0 if success else 1)
