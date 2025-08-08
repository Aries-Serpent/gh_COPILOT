from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Dict, Iterator

from . import logger, store_state


class SchemaMapper:
    """Apply updates to a schema with conflict resolution strategies."""

    def __init__(self, base_schema: Dict[str, Any]) -> None:
        self.schema = base_schema

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Provide a transactional context with rollback support."""
        snapshot = deepcopy(self.schema)
        store_state(snapshot)
        try:
            yield
        except Exception:
            from . import rollback
            restored = rollback()
            self.schema = restored if restored is not None else snapshot
            raise

    @staticmethod
    def _schema_mismatch(current: Any, incoming: Any) -> bool:
        """Return True if the types of the values do not match."""
        return type(current) is not type(incoming)

    def apply(self, updates: Dict[str, Any], strategy: str = "merge") -> Dict[str, Any]:
        """Apply updates to the schema using the given conflict strategy."""
        strategy = strategy.lower()
        with self.transaction():
            for key, value in updates.items():
                if key in self.schema and self.schema[key] != value:
                    logger.info("Conflict detected for '%s'", key)
                    if self._schema_mismatch(self.schema[key], value):
                        logger.info("Schema mismatch for '%s'", key)
                        if strategy == "merge":
                            logger.info("Merge skipped for '%s'; keeping original", key)
                            continue
                        if strategy == "overwrite":
                            self.schema[key] = value
                            logger.info("Overwrote '%s'", key)
                            continue
                        if strategy == "manual":
                            logger.info("Manual resolution required for '%s'", key)
                            raise ValueError(f"Manual resolution required for '{key}'")
                        raise ValueError(f"Unknown strategy '{strategy}'")
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
