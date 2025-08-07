#!/usr/bin/env python3
"""Daemon script to keep production and staging databases synchronized."""

from pathlib import Path

from database_first_synchronization_engine import watch_and_sync


def main() -> None:
    """Run watch_and_sync on production and staging databases."""
    production = Path("databases/production.db")
    staging = Path("databases/staging.db")
    try:
        watch_and_sync(production, staging)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
