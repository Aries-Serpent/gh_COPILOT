#!/usr/bin/env python3
"""Bootstrap environment and ensure test requirements are installed."""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Iterable
import logging

from . import run_migrations


def ensure_env() -> None:
    """Create `.env` from `.env.example` when needed."""
    repo_root = Path(__file__).resolve().parents[1]
    env_file = repo_root / ".env"
    example_file = repo_root / ".env.example"

    if env_file.exists():
        print(".env already present")
    elif example_file.exists():
        shutil.copy(example_file, env_file)
        print("Created .env from .env.example")
    else:
        msg = ".env.example not found. Please create it from documentation."
        logging.warning(msg)
        raise FileNotFoundError(msg)


def _parse_requirements(path: Path) -> Iterable[str]:
    """Return a list of requirement strings from ``requirements-test.txt``."""
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield stripped


def install_test_requirements() -> None:
    """Install dependencies required for running tests."""
    repo_root = Path(__file__).resolve().parents[1]
    requirements = repo_root / "requirements-test.txt"

    if not requirements.exists():
        print("requirements-test.txt not found; skipping test dependency installation")
        return

    packages = list(_parse_requirements(requirements))

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *packages,
        ]
    )
    print("Installed test dependencies: " + ", ".join(packages))


def verify_migrations() -> None:
    """Ensure all SQL migrations have been applied."""
    repo_root = Path(__file__).resolve().parents[1]
    migrations_dir = repo_root / "databases" / "migrations"
    db_path = repo_root / "databases" / "analytics.db"

    if not migrations_dir.exists():
        print("No migrations directory found; skipping migration verification")
        return

    run_migrations.ensure_migrations_applied()

    if not db_path.exists():
        raise FileNotFoundError("analytics.db missing after migration run")

    with sqlite3.connect(db_path) as conn:
        applied = {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}

    missing = [p.name for p in migrations_dir.glob("*.sql") if p.name not in applied]
    if missing:
        raise RuntimeError(f"Unapplied migrations: {', '.join(missing)}")
    print("Migrations verified")


def main() -> None:
    """Bootstrap environment and install test requirements."""
    ensure_env()
    install_test_requirements()
    verify_migrations()


if __name__ == "__main__":
    main()
