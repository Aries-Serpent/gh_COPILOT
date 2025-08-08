import logging
from copy import deepcopy
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_snapshot: Optional[Dict[str, Any]] = None


def store_state(state: Dict[str, Any]) -> None:
    """Store a pre-conflict snapshot for potential rollback."""
    global _snapshot
    _snapshot = deepcopy(state)


def rollback() -> Optional[Dict[str, Any]]:
    """Rollback schema changes in case of failure.

    Returns the stored snapshot so callers can restore state.
    """
    logger.info("Schema rollback executed")
    return deepcopy(_snapshot) if _snapshot is not None else None
