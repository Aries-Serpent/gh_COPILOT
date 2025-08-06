"""Deprecated wrapper for placeholder cleanup.

Use ``scripts/code_placeholder_audit.py --cleanup`` which now provides
``--rollback-id`` and ``--summary-json`` options.
"""

from __future__ import annotations

import sys

from utils.validation_utils import anti_recursion_guard
from scripts import code_placeholder_audit

@anti_recursion_guard
def main() -> None:
    print(
        "DEPRECATED: use 'python scripts/code_placeholder_audit.py --apply-fixes'",
        file=sys.stderr,
    )
    code_placeholder_audit.main(*sys.argv[1:])


if __name__ == "__main__":
    main()
