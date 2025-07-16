"""
Database configuration and models.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""
    database_path: Path
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        if isinstance(self.database_path, str):
            self.database_path = Path(self.database_path)