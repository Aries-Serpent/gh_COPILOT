"""Enterprise secret management utilities."""

from __future__ import annotations

import os
from typing import Optional


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve secret from environment variables securely."""
    value = os.getenv(name, default)
    return value
