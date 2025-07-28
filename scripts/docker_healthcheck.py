#!/usr/bin/env python3
"""Simple health check for Docker container."""

from utils.validation_utils import validate_enterprise_environment

if __name__ == "__main__":
    try:
        validate_enterprise_environment()
    except Exception:
        raise SystemExit(1)
    raise SystemExit(0)
