"""Thin wrapper for :mod:"scripts.database.unified_database_management_system"."""
from scripts.database.unified_database_management_system import (
    UnifiedDatabaseManager, synchronize_databases)

__all__ = ["UnifiedDatabaseManager", "synchronize_databases"]
