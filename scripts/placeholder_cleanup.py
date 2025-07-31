"""Deprecated wrapper for placeholder cleanup.

Use ``scripts/code_placeholder_audit.py --cleanup`` which now provides
``--rollback-id`` and ``--summary-json`` options.
"""

from __future__ import annotations

import sys
from scripts import code_placeholder_audit

if __name__ == "__main__":
    print(
        "DEPRECATED: use 'python scripts/code_placeholder_audit.py --apply-fixes'",
        file=sys.stderr,
    )
    code_placeholder_audit.main(*sys.argv[1:])
