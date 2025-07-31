"""Deprecated wrapper for placeholder cleanup.

Please run ``scripts/code_placeholder_audit.py --cleanup`` instead."""

from __future__ import annotations

import sys
from scripts import code_placeholder_audit

if __name__ == "__main__":
    print(
        "DEPRECATED: use 'python scripts/code_placeholder_audit.py --cleanup'",
        file=sys.stderr,
    )
    code_placeholder_audit.main(*sys.argv[1:])
