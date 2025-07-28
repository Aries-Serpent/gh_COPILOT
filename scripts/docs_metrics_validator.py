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

if __package__ in {None, ""}:
    # Allow running as a script directly without module context
    SCRIPT_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(SCRIPT_DIR))
    from validate_docs_metrics import validate, DB_PATH  # type: ignore
else:  # pragma: no cover - executed when imported as package module
    from .validate_docs_metrics import validate, DB_PATH


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
        default=DB_PATH,
        help="Path to the production database",
    )
    args = parser.parse_args(argv)
    success = validate(args.db_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
