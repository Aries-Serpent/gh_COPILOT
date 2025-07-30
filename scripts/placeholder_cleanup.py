"""Deprecated wrapper for placeholder cleanup.

Use ``scripts.code_placeholder_audit`` with ``--cleanup`` instead."""
from __future__ import annotations

import sys
from scripts import code_placeholder_audit

if __name__ == "__main__":
    code_placeholder_audit.main(*sys.argv[1:])

