"""Staging configuration for web GUI scripts.

Follows the pattern of the production configuration with
settings suited for the staging environment.
"""

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "databases"


@dataclass
class StagingConfig:
    """Configuration values for staging environment."""

    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_PATH: str = str(DATABASE_DIR / "staging.db")
