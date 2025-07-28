"""Deprecated wrapper for :mod:`scripts.code_placeholder_audit`."""

from __future__ import annotations

from .code_placeholder_audit import main

__all__ = ["main"]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audit workspace for TODO/FIXME placeholders")
    parser.add_argument("--workspace-path", type=str, help="Workspace to scan")
    parser.add_argument("--analytics-db", type=str, help="analytics.db location")
    parser.add_argument("--production-db", type=str, help="production.db location")
    parser.add_argument("--dashboard-dir", type=str, help="dashboard/compliance directory")
    parser.add_argument("--timeout-minutes", type=int, default=30, help="Scan timeout in minutes")
    parser.add_argument("--simulate", action="store_true", help="Run in test mode without writes")
    args = parser.parse_args()

    success = main(
        workspace_path=args.workspace_path,
        analytics_db=args.analytics_db,
        production_db=args.production_db,
        dashboard_dir=args.dashboard_dir,
        timeout_minutes=args.timeout_minutes,
        simulate=args.simulate,
    )
    raise SystemExit(0 if success else 1)
