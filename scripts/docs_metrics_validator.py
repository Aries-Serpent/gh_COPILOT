#!/usr/bin/env python3
"""Compatibility wrapper for documentation metrics validation.

This script delegates to :mod:`validate_docs_metrics` to ensure
backwards compatibility with existing CI workflows expecting
``docs_metrics_validator.py``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import validate_docs_metrics


def main(argv: list[str] | None = None) -> int:
    """Entry point for docs metrics validation.

    Parameters
    ----------
    argv: list[str] | None
        Optional command line arguments. If ``None``, ``sys.argv[1:]`` is used.
    """
    parser = argparse.ArgumentParser(description="Validate documentation metrics")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=validate_docs_metrics.DB_PATH,
        help="Path to the production database",
    )
    args = parser.parse_args(argv)
    success = validate_docs_metrics.validate(args.db_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
