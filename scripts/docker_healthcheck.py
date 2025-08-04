#!/usr/bin/env python3
"""Simple health check for Docker container.

This script validates the enterprise environment and ensures the Flask
dashboard is responding on the configured port.
"""

from __future__ import annotations

import os
from urllib.request import urlopen

from utils.validation_utils import anti_recursion_guard, validate_enterprise_environment


def check_health() -> bool:
    """Return ``True`` if the dashboard health endpoint responds successfully."""
    validate_enterprise_environment()
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    try:
        with urlopen(f"http://localhost:{port}/health", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


@anti_recursion_guard
def main() -> int:
    """Run the health check and return an exit code."""
    return 0 if check_health() else 1


if __name__ == "__main__":
    raise SystemExit(main())
