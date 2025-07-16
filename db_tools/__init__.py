"""
Database Tools Package

Unified database utilities for the gh_COPILOT toolkit.
Provides modular database access, cleanup, and compliance checking capabilities.
"""

__version__ = "1.0.0"

# Import main classes for easy access
from .core.connection import DatabaseConnection
from .core.exceptions import DatabaseError, DatabaseConnectionError
from .operations.access import DatabaseAccessLayer
from .operations.cleanup import DatabaseCleanupProcessor
from .operations.compliance import DatabaseComplianceChecker

__all__ = [
    'DatabaseConnection',
    'DatabaseError', 
    'DatabaseConnectionError',
    'DatabaseAccessLayer',
    'DatabaseCleanupProcessor',
    'DatabaseComplianceChecker'
]