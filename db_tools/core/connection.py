"""
Unified database connection management for the gh_COPILOT toolkit.
Extracted from database access layer, cleanup processor, and compliance checker.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Union, Any, Dict
from contextlib import contextmanager

from .exceptions import DatabaseConnectionError, DatabaseQueryError
from .models import DatabaseConfig


class DatabaseConnection:
    """Unified database connection manager"""
    
    def __init__(self, config: Union[DatabaseConfig, str, Path]):
        if isinstance(config, (str, Path)):
            config = DatabaseConfig(database_path=Path(config))
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.config.database_path,
                timeout=self.config.timeout
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise DatabaseConnectionError(f"Database connection failed: {e}")
        finally:
            if conn:
                conn.close()
                
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        """Execute a single query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            raise DatabaseQueryError(f"Query execution failed: {e}")
            
    def execute_many(self, query: str, params_list: list) -> int:
        """Execute query with multiple parameter sets"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            raise DatabaseQueryError(f"Batch query execution failed: {e}")
            
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database"""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return len(result) > 0