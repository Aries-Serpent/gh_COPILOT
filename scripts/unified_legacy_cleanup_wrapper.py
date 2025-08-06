#!/usr/bin/env python3
"""Wrapper for scheduling Unified Legacy Cleanup System runs.

This script provides a thin CLI around :class:`unified_legacy_cleanup_system.UnifiedLegacyCleanupSystem`
so it can be invoked by schedulers or shell scripts. It supports optional
workspace selection and dry-run mode.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from unified_legacy_cleanup_system import UnifiedLegacyCleanupSystem


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Legacy Cleanup Wrapper")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace root to scan")
    parser.add_argument("--dry-run", action="store_true", help="Perform cleanup without changing files")
    return parser.parse_args(args)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    system = UnifiedLegacyCleanupSystem(ns.workspace)
    system.run_cleanup(dry_run=ns.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
