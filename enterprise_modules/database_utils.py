#!/usr/bin/env python3
"""
Enterprise Database Utils Module
gh_COPILOT Toolkit - Modular Architecture

Database operation utilities extracted from 4 enterprise scripts
Standardized database connections and query operations

Usage:
    from enterprise_modules.database_utils import get_enterprise_database_connection, execute_safe_query
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


def get_enterprise_database_connection(
    db_path: str = "production.db",
    timeout: float = 30.0,
    check_same_thread: bool = False
) -> Optional[sqlite3.Connection]:
    """
    Get standardized enterprise database connection
    
    Extracted from scripts:
    - script_modulation_analyzer.py
    - enterprise_file_relocation_orchestrator.py
    - database_mapping_updater.py
    - database_schema_final_completion.py
    """
    try:
        db_file = Path(db_path)
        
        if not db_file.exists():
            logging.warning(f"Database file does not exist: {db_path}")
            # Create database if it doesn't exist
            db_file.parent.mkdir(parents=True, exist_ok=True)
        
        connection = sqlite3.connect(
            str(db_file),
            timeout=timeout,
            check_same_thread=check_same_thread
        )
        
        # Enable foreign key constraints
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory for easier access
        connection.row_factory = sqlite3.Row
        
        logging.info(f"Database connection established: {db_path}")
        return connection
        
    except Exception as e:
        logging.error(f"Error connecting to database {db_path}: {e}")
        return None


@contextmanager
def enterprise_database_context(
    db_path: str = "production.db",
    timeout: float = 30.0
):
    """
    Context manager for enterprise database operations
    """
    connection = None
    try:
        connection = get_enterprise_database_connection(db_path, timeout)
        if connection:
            yield connection
        else:
            raise Exception(f"Could not establish database connection to {db_path}")
    except Exception as e:
        logging.error(f"Database context error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def execute_safe_query(
    connection: sqlite3.Connection,
    query: str,
    parameters: Tuple = (),
    fetch_all: bool = True
) -> Optional[List[sqlite3.Row]]:
    """
    Execute database query with error handling
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        
        if fetch_all:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()
            
        return results
        
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        logging.error(f"Query: {query}")
        logging.error(f"Parameters: {parameters}")
        return None


def execute_safe_insert(
    connection: sqlite3.Connection,
    table_name: str,
    data: Dict[str, Any],
    commit: bool = True
) -> bool:
    """
    Execute safe insert operation
    """
    try:
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        cursor = connection.cursor()
        cursor.execute(query, values)
        
        if commit:
            connection.commit()
        
        logging.info(f"Inserted record into {table_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error inserting into {table_name}: {e}")
        connection.rollback()
        return False


def execute_safe_update(
    connection: sqlite3.Connection,
    table_name: str,
    data: Dict[str, Any],
    where_clause: str,
    where_params: Tuple = (),
    commit: bool = True
) -> bool:
    """
    Execute safe update operation
    """
    try:
        set_clauses = [f"{column} = ?" for column in data.keys()]
        values = list(data.values()) + list(where_params)
        
        query = f"""
        UPDATE {table_name}
        SET {', '.join(set_clauses)}
        WHERE {where_clause}
        """
        
        cursor = connection.cursor()
        cursor.execute(query, values)
        
        if commit:
            connection.commit()
        
        rows_affected = cursor.rowcount
        logging.info(f"Updated {rows_affected} rows in {table_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating {table_name}: {e}")
        connection.rollback()
        return False


def check_table_exists(
    connection: sqlite3.Connection,
    table_name: str
) -> bool:
    """
    Check if table exists in database
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        result = cursor.fetchone()
        return result is not None
        
    except Exception as e:
        logging.error(f"Error checking if table {table_name} exists: {e}")
        return False


def get_table_schema(
    connection: sqlite3.Connection,
    table_name: str
) -> List[Dict[str, Any]]:
    """
    Get table schema information
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        
        schema_info = []
        for row in cursor.fetchall():
            schema_info.append({
                'column_id': row[0],
                'name': row[1],
                'type': row[2],
                'not_null': bool(row[3]),
                'default_value': row[4],
                'primary_key': bool(row[5])
            })
        
        return schema_info
        
    except Exception as e:
        logging.error(f"Error getting schema for table {table_name}: {e}")
        return []


def backup_database(
    source_db_path: str,
    backup_db_path: str
) -> bool:
    """
    Create database backup
    """
    try:
        source_path = Path(source_db_path)
        backup_path = Path(backup_db_path)
        
        if not source_path.exists():
            logging.error(f"Source database does not exist: {source_db_path}")
            return False
        
        # Create backup directory
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy database
        import shutil
        shutil.copy2(source_path, backup_path)
        
        logging.info(f"Database backup created: {backup_db_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error creating database backup: {e}")
        return False


# Enterprise Module Metadata
__version__ = "1.0.0"
__author__ = "gh_COPILOT Enterprise Toolkit"
__description__ = "Database operation utilities for enterprise scripts"
__extracted_from_scripts__ = 4
__lines_saved__ = 60
__implementation_priority__ = "MEDIUM"
