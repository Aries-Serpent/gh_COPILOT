"""Bootstrap environment and ensure test requirements are installed."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


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
        raise FileNotFoundError("Missing .env.example")


def install_test_requirements() -> None:
    """Install dependencies required for running tests."""
    repo_root = Path(__file__).resolve().parents[1]
    requirements = repo_root / "requirements-test.txt"

    if not requirements.exists():
        print("requirements-test.txt not found; skipping test dependency installation")
        return

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements)]
    )
    print("Installed test dependencies")


def main() -> None:
    """Bootstrap environment and install test requirements."""
    ensure_env()
    install_test_requirements()


if __name__ == "__main__":
    main()
