#!/usr/bin/env python3
"""Codex log database utilities.

This module provides helpers to initialize and append to a dedicated
``codex_logs.db`` SQLite database. Each log entry captures the action and
statement issued by Codex during a session. The resulting database can be
committed for post-session analysis and lessons learned processing.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

DEFAULT_DB_PATH = Path("databases/codex_logs.db")


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Ensure the codex log database exists with the proper schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                statement TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_action(action: str, statement: str, *, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Record a codex action and statement into the database."""
    init_db(db_path)
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO codex_logs (timestamp, action, statement) VALUES (?, ?, ?)",
            (timestamp, action, statement),
        )
        conn.commit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Codex log database helper")
    parser.add_argument("--action", help="Action performed by Codex")
    parser.add_argument("--statement", help="Associated statement")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize the database and exit",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to codex log database",
    )
    args = parser.parse_args()
    if args.init:
        init_db(args.db_path)
    elif args.action and args.statement:
        log_action(args.action, args.statement, db_path=args.db_path)
    else:
        parser.error("Provide --init or both --action and --statement")
