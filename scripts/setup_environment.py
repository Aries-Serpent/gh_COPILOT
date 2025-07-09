"""Utility to ensure a `.env` file exists.

This script copies `.env.example` to `.env` if the latter is missing.
"""
import shutil
from pathlib import Path


def main() -> None:
    """Create `.env` from `.env.example` when needed."""
    repo_root = Path(__file__).resolve().parents[1]
    env_file = repo_root / ".env"
    example_file = repo_root / ".env.example"

    if env_file.exists():
        print(".env already present")
        return

    if not example_file.exists():
        raise FileNotFoundError("Missing .env.example")

    shutil.copy(example_file, env_file)
    print("Created .env from .env.example")


if __name__ == "__main__":
    main()
