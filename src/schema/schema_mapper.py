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

    def _resolve(
        self, current: Any, incoming: Any, path: str, strategy: str
    ) -> Any:
        """Resolve conflicts between current and incoming values."""
        if current is None:
            return incoming
        if current == incoming:
            return current

        logger.info("Conflict detected for '%s'", path)
        if self._schema_mismatch(current, incoming):
            logger.info("Schema mismatch for '%s'", path)
            if strategy == "merge":
                logger.info("Merge skipped for '%s'; keeping original", path)
                return current
            if strategy == "overwrite":
                logger.info("Overwrote '%s'", path)
                return incoming
            if strategy == "manual":
                logger.info("Manual resolution required for '%s'", path)
                raise ValueError(f"Manual resolution required for '{path}'")
            raise ValueError(f"Unknown strategy '{strategy}'")

        if isinstance(current, dict) and isinstance(incoming, dict):
            result: Dict[str, Any] = dict(current)
            for key, value in incoming.items():
                sub_path = f"{path}.{key}" if path else key
                result[key] = self._resolve(current.get(key), value, sub_path, strategy)
            return result

        if strategy == "merge":
            logger.info("Merge skipped for '%s'; keeping original", path)
            return current
        if strategy == "overwrite":
            logger.info("Overwrote '%s'", path)
            return incoming
        if strategy == "manual":
            logger.info("Manual resolution required for '%s'", path)
            raise ValueError(f"Manual resolution required for '{path}'")
        raise ValueError(f"Unknown strategy '{strategy}'")

    def apply(self, updates: Dict[str, Any], strategy: str = "merge") -> Dict[str, Any]:
        """Apply updates to the schema using the given conflict strategy."""
        strategy = strategy.lower()
        with self.transaction():
            for key, value in updates.items():
                self.schema[key] = self._resolve(
                    self.schema.get(key), value, key, strategy
                )
        return self.schema
