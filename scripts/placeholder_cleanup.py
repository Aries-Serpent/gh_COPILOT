"""Placeholder Cleanup CLI.

This script orchestrates placeholder auditing, removal, logging, and dashboard
updates. It uses :mod:`scripts.code_placeholder_audit` for detection and
:mod:`template_engine.template_placeholder_remover` for cleanup.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import json
from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
from scripts import code_placeholder_audit as audit


def run(
    workspace: Path,
    analytics_db: Path,
    production_db: Path,
    dashboard_dir: Path,
    *,
    timeout_minutes: int = 30,
    cleanup: bool = False,
    dry_run: bool = False,
) -> bool:
    patterns = (
        audit.DEFAULT_PATTERNS
        + audit.fetch_db_placeholders(production_db)
        + audit.load_best_practice_patterns()
    )
    results = audit.scan_files(workspace, patterns, timeout_minutes * 60)
    audit.log_findings(results, analytics_db, simulate=dry_run)
    if cleanup and not dry_run:
        audit.auto_remove_placeholders(results, production_db, analytics_db)
        audit.log_findings([], analytics_db, update_resolutions=True)
    if not dry_run:
        ComplianceMetricsUpdater(dashboard_dir).update()
    return audit.validate_results(0 if cleanup else len(results), analytics_db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and clean placeholders")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("analytics_db", type=Path)
    parser.add_argument("production_db", type=Path)
    parser.add_argument("dashboard_dir", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--cleanup", action="store_true", help="Remove placeholders")
    parser.add_argument("--dry-run", action="store_true", help="Run without DB writes")
    parser.add_argument("--rollback-last", action="store_true", help="Rollback last audit")
    args = parser.parse_args()
    if args.rollback_last:
        if audit.rollback_last_entry(args.analytics_db):
            print("Rollback complete")
            raise SystemExit(0)
        raise SystemExit(1)
    success = run(
        args.workspace,
        args.analytics_db,
        args.production_db,
        args.dashboard_dir,
        timeout_minutes=args.timeout,
        cleanup=args.cleanup,
        dry_run=args.dry_run,
    )
    summary = {
        "workspace": str(args.workspace),
        "cleanup": args.cleanup,
        "dry_run": args.dry_run,
        "result": success,
    }
    print(json.dumps(summary))
    raise SystemExit(0 if success else 1)
