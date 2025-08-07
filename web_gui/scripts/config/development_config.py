"""Development configuration for web GUI scripts.

Mirrors the structure of the production configuration with
settings tailored for local development.
"""

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "databases"


@dataclass
class DevelopmentConfig:
    """Configuration values for development environment."""

    DEBUG: bool = True
    TESTING: bool = True
    DATABASE_PATH: str = str(DATABASE_DIR / "development.db")
