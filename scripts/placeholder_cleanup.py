"""Deprecated placeholder cleanup wrapper.

This thin wrapper forwards arguments to :mod:`scripts.code_placeholder_audit`.
Use ``scripts/code_placeholder_audit.py`` directly for all operations.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import json
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
    return audit.main(
        workspace_path=str(workspace),
        analytics_db=str(analytics_db),
        production_db=str(production_db),
        dashboard_dir=str(dashboard_dir),
        timeout_minutes=timeout_minutes,
        simulate=dry_run,
        apply_fixes=cleanup,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and clean placeholders")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("analytics_db", type=Path)
    parser.add_argument("production_db", type=Path)
    parser.add_argument("dashboard_dir", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--cleanup", action="store_true", help="Remove placeholders")
    parser.add_argument("--dry-run", action="store_true", help="Run without DB writes")
    parser.add_argument("--force", action="store_true", help="Force cleanup when not in dry-run mode")
    parser.add_argument("--rollback-last", action="store_true", help="Rollback last audit")
    args = parser.parse_args()
    if args.rollback_last:
        result = audit.rollback_last_entry(args.analytics_db)
        print(json.dumps({"rollback": result}))
        raise SystemExit(0 if result else 1)

    if args.cleanup and not (args.dry_run or args.force):
        print(json.dumps({"error": "--cleanup requires --force when not in dry-run"}))
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
        "success": success,
    }
    print(json.dumps(summary))
    raise SystemExit(0 if success else 1)
