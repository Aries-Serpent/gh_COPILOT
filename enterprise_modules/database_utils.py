#!/usr/bin/env python3
"""
Enterprise Database Utils Module
gh_COPILOT Toolkit - Modular Architecture

Database operation utilities extracted from 4 enterprise scripts
Standardized database connections and query operations

Usage:
    from enterprise_modules.database_utils import get_enterprise_database_connection, execute_safe_query
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union, Iterator
from contextlib import contextmanager

from enterprise_modules.compliance import (
    ComplianceError,
    anti_recursion_guard,
    validate_enterprise_operation,
)


def get_enterprise_database_connection(
    db_path: str = "production.db",
    timeout: float = 30.0,
    check_same_thread: bool = False
) -> Optional[sqlite3.Connection]:
    """
    Get standardized enterprise database connection

    Connections run in WAL mode with a configurable busy timeout to
    support concurrent access.
    
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
            check_same_thread=check_same_thread,
        )
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
        connection.execute("PRAGMA foreign_keys = ON")
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
) -> Iterator[sqlite3.Connection]:
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


@anti_recursion_guard
def execute_safe_insert(
    connection: sqlite3.Connection,
    table_name: str,
    data: Dict[str, Any],
    commit: bool = True
) -> bool:
    """Execute safe insert operation with enterprise validation."""
    db_file = Path(
        connection.execute("PRAGMA database_list").fetchone()[2]
    )
    if not validate_enterprise_operation(str(db_file)):
        raise ComplianceError(f"Forbidden database write: {db_file}")

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


def execute_safe_batch_insert(
    connection: sqlite3.Connection,
    table_name: str,
    rows: List[Dict[str, Any]],
    *,
    chunk_size: Optional[int] = None,
    checkpoint_interval: Optional[int] = None,
) -> bool:
    """Insert multiple rows efficiently with optional chunking.

    Parameters
    ----------
    connection:
        Target SQLite connection.
    table_name:
        Name of the table to insert into.
    rows:
        Sequence of dictionaries representing rows to insert.
    chunk_size:
        When provided, commit after each chunk of this size.
    checkpoint_interval:
        Run a WAL checkpoint after roughly this many rows.
    """

    if not rows:
        return True
    db_file = Path(connection.execute("PRAGMA database_list").fetchone()[2])
    try:
        if not validate_enterprise_operation(str(db_file)):
            raise ComplianceError(f"Forbidden database write: {db_file}")
    except NotADirectoryError as exc:  # pragma: no cover - safety net
        logging.error("Validation path error: %s", exc)

    columns = list(rows[0].keys())
    placeholder_str = ", ".join("?" for _ in columns)
    query = (
        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholder_str})"
    )
    values = [tuple(r[c] for c in columns) for r in rows]

    try:
        cursor = connection.cursor()
        if not chunk_size:
            cursor.executemany(query, values)
            connection.commit()
            if checkpoint_interval:
                wal_checkpoint(connection)
        else:
            processed = 0
            for i in range(0, len(values), chunk_size):
                chunk = values[i : i + chunk_size]
                cursor.executemany(query, chunk)
                connection.commit()
                processed += len(chunk)
                if checkpoint_interval and processed >= checkpoint_interval:
                    wal_checkpoint(connection)
                    processed = 0
        logging.info(f"Inserted {len(values)} records into {table_name}")
        return True
    except Exception as e:
        logging.error(f"Error batch inserting into {table_name}: {e}")
        connection.rollback()
        return False


def wal_checkpoint(connection: sqlite3.Connection, mode: str = "PASSIVE") -> None:
    """Trigger a WAL checkpoint on the given connection."""
    try:
        connection.execute(f"PRAGMA wal_checkpoint({mode})")
    except Exception as e:
        logging.warning(f"WAL checkpoint failed: {e}")


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


def fetch_template(
    name: str,
    db_path: Union[str, Path, None] = None,
) -> Optional[str]:
    """Return template body from ``production.db`` if present.

    Parameters
    ----------
    name:
        Template identifier to fetch.
    db_path:
        Optional path to the database. When not provided, defaults to
        ``<GH_COPILOT_WORKSPACE>/databases/production.db``.
    """

    workspace = Path(
        os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
    )
    db_file = Path(db_path) if db_path else workspace / "databases" / "production.db"

    with enterprise_database_context(str(db_file)) as conn:
        row = execute_safe_query(
            conn,
            "SELECT template_content FROM template_repository WHERE template_name = ?",
            (name,),
            fetch_all=False,
        )
        if row:
            return row["template_content"]

        row = execute_safe_query(
            conn,
            "SELECT base_template FROM script_templates WHERE template_name = ?",
            (name,),
            fetch_all=False,
        )
        if row:
            return row["base_template"]

    return None


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


@anti_recursion_guard
def backup_database(
    source_db_path: str,
    backup_db_path: str
) -> bool:
    """Create database backup with enterprise validation."""
    backup_path = Path(backup_db_path)
    if not validate_enterprise_operation(str(backup_path)):
        raise ComplianceError(f"Forbidden backup target: {backup_path}")

    try:
        source_path = Path(source_db_path)

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
