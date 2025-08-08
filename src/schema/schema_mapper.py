from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Dict

from . import logger


class SchemaMapper:
    """Apply updates to a schema with conflict resolution strategies."""

    def __init__(self, base_schema: Dict[str, Any]):
        self.schema = base_schema

    @contextmanager
    def transaction(self):
        """Provide a transactional context with rollback support."""
        snapshot = deepcopy(self.schema)
        try:
            yield
        except Exception:
            from . import rollback
            rollback()
            self.schema = snapshot
            raise

    def apply(self, updates: Dict[str, Any], strategy: str = "merge") -> Dict[str, Any]:
        """Apply updates to the schema using the given conflict strategy."""
        strategy = strategy.lower()
        with self.transaction():
            for key, value in updates.items():
                if key in self.schema and self.schema[key] != value:
                    logger.info("Conflict detected for '%s'", key)
                    if strategy == "merge":
                        if isinstance(self.schema[key], dict) and isinstance(value, dict):
                            self.schema[key] = {**self.schema[key], **value}
                            logger.info("Merged '%s'", key)
                        else:
                            logger.info("Merge skipped for '%s'; keeping original", key)
                    elif strategy == "overwrite":
                        self.schema[key] = value
                        logger.info("Overwrote '%s'", key)
                    elif strategy == "manual":
                        logger.info("Manual resolution required for '%s'", key)
                        raise ValueError(f"Manual resolution required for '{key}'")
                    else:
                        raise ValueError(f"Unknown strategy '{strategy}'")
                else:
                    self.schema[key] = value
        return self.schema
