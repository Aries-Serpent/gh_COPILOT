#!/usr/bin/env python3
# [Session]: Unified Session Management System
# > Generated: 2025-07-24 20:23:55 | Author: mbaetiong

"""
Unified Session Management System

- Provides a unified interface for session discovery, loading, consolidation, and atomic writing.
- Supports multiple storage backends (SQLite, JSON, CSV) for enterprise session data.
- Ensures transactional safety and audit logging for all operations.
- Enables external tools to interact with session data via API functions.
"""

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from utils.log_utils import _log_event

TEXT_INDICATORS = {
    "start": "[START]",
    "progress": "[PROGRESS]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "atomic": "[ATOMIC]",
}


def discover_active_sessions(db_file: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Discover and return all active sessions in the session database.
    Supports SQLite3 files and JSON/CSV session exports.

    Returns a list of session dictionaries.
    """
    db_file = Path(db_file)
    if db_file.suffix == ".db" or db_file.suffix == ".sqlite3":
        sessions = []
        try:
            with sqlite3.connect(str(db_file)) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT session_id, user_id, state, created_at, "
                    "last_updated, metadata FROM sessions WHERE state='active';"
                )
                for row in cur.fetchall():
                    session_id, user_id, state, created_at, last_updated, metadata = row
                    try:
                        meta_obj = json.loads(metadata)
                    except Exception:
                        meta_obj = metadata if metadata else {}
                    sessions.append({
                        "session_id": session_id,
                        "user_id": user_id,
                        "state": state,
                        "created_at": created_at,
                        "last_updated": last_updated,
                        "metadata": meta_obj,
                    })
        except Exception as e:
            _log_event({"event": "session_discovery_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to discover sessions: {e}")
        return sessions
    elif db_file.suffix == ".json":
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                records = json.load(f)
            # Filter to active sessions
            return [rec for rec in records if rec.get("state") == "active"]
        except Exception as e:
            _log_event({"event": "session_discovery_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to read JSON: {e}")
            return []
    elif db_file.suffix == ".csv":
        try:
            sessions = []
            with open(db_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("state") == "active":
                        try:
                            meta_obj = json.loads(row.get("metadata", "{}"))
                        except Exception:
                            meta_obj = row.get("metadata", {})
                        row["metadata"] = meta_obj
                        sessions.append(row)
            return sessions
        except Exception as e:
            _log_event({"event": "session_discovery_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to read CSV: {e}")
            return []
    else:
        print(f"{TEXT_INDICATORS['error']} Unsupported session storage format: {db_file}")
        _log_event({"event": "session_discovery_failed", "error": "unsupported format"})
        return []


def consolidate_sessions_atomic(
    session_list: List[Dict[str, Any]],
    output_db: Union[str, Path],
    overwrite: bool = True,
    backup_dir: Optional[Union[str, Path]] = None
) -> None:
    """
    Atomically consolidates given session records to the output SQLite database.
    - Optionally backs up the existing output DB.
    - Overwrites the output DB if requested.
    - Ensures all records are written in a single transaction.
    """
    output_db = Path(output_db)
    if backup_dir:
        backup_dir = Path(backup_dir)
    if output_db.exists() and backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{output_db.stem}_backup_{timestamp}{output_db.suffix}"
        backup_file.write_bytes(output_db.read_bytes())
        print(f"{TEXT_INDICATORS['info']} Output session DB backed up to {backup_file}")

    if output_db.exists() and overwrite:
        output_db.unlink()
        print(f"{TEXT_INDICATORS['atomic']} Overwrote existing {output_db}")

    # Create new DB and table
    with sqlite3.connect(str(output_db)) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                metadata TEXT
            );
        """)
        # Perform atomic insert
        conn.execute("BEGIN TRANSACTION;")
        for session in session_list:
            try:
                cur.execute("""
                    INSERT OR REPLACE INTO sessions (session_id, user_id, state, created_at, last_updated, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.get("session_id"),
                    session.get("user_id"),
                    session.get("state"),
                    session.get("created_at"),
                    session.get("last_updated"),
                    json.dumps(session.get("metadata", {})),
                ))
            except Exception as e:
                _log_event(
                    {
                        "event": "session_consolidation_insert_failed",
                        "error": str(e),
                        "session_id": session.get("session_id"),
                    }
                )
                print(
                    f"{TEXT_INDICATORS['error']} Failed to consolidate session {session.get('session_id')}: {e}"
                )
        conn.commit()
    _log_event(
        {
            "event": "session_consolidation_atomic_complete",
            "output_db": str(output_db),
            "count": len(session_list),
        }
    )
    print(f"{TEXT_INDICATORS['success']} Atomically wrote {len(session_list)} consolidated sessions to {output_db}")


def get_session_by_id(db_file: Union[str, Path], session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single session by ID from a SQLite, JSON, or CSV session database.
    Returns session dict or None if not found.
    """
    db_file = Path(db_file)
    if db_file.suffix in (".db", ".sqlite3"):
        try:
            with sqlite3.connect(str(db_file)) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT session_id, user_id, state, created_at, last_updated, "
                    "metadata FROM sessions WHERE session_id=?;",
                    (session_id,),
                )
                row = cur.fetchone()
                if row:
                    session_id, user_id, state, created_at, last_updated, metadata = row
                    try:
                        meta_obj = json.loads(metadata)
                    except Exception:
                        meta_obj = metadata if metadata else {}
                    return {
                        "session_id": session_id,
                        "user_id": user_id,
                        "state": state,
                        "created_at": created_at,
                        "last_updated": last_updated,
                        "metadata": meta_obj,
                    }
        except Exception as e:
            _log_event({"event": "get_session_by_id_failed", "error": str(e), "session_id": session_id})
            print(f"{TEXT_INDICATORS['error']} Failed to retrieve session {session_id}: {e}")
    elif db_file.suffix == ".json":
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                records = json.load(f)
            for rec in records:
                if rec.get("session_id") == session_id:
                    return rec
        except Exception as e:
            _log_event({"event": "get_session_by_id_failed", "error": str(e), "session_id": session_id})
    elif db_file.suffix == ".csv":
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("session_id") == session_id:
                        try:
                            row["metadata"] = json.loads(row.get("metadata", "{}"))
                        except Exception:
                            pass
                        return row
        except Exception as e:
            _log_event({"event": "get_session_by_id_failed", "error": str(e), "session_id": session_id})
    else:
        print(f"{TEXT_INDICATORS['error']} Unsupported session storage format: {db_file}")
    return None


def list_all_sessions(db_file: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    List all sessions from the given session storage backend (SQLite, JSON, or CSV).
    """
    db_file = Path(db_file)
    sessions = []
    if db_file.suffix in (".db", ".sqlite3"):
        try:
            with sqlite3.connect(str(db_file)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT session_id, user_id, state, created_at, last_updated, metadata FROM sessions;")
                for row in cur.fetchall():
                    session_id, user_id, state, created_at, last_updated, metadata = row
                    try:
                        meta_obj = json.loads(metadata)
                    except Exception:
                        meta_obj = metadata if metadata else {}
                    sessions.append({
                        "session_id": session_id,
                        "user_id": user_id,
                        "state": state,
                        "created_at": created_at,
                        "last_updated": last_updated,
                        "metadata": meta_obj,
                    })
        except Exception as e:
            _log_event({"event": "list_all_sessions_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to list sessions: {e}")
            return []
    elif db_file.suffix == ".json":
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                sessions = json.load(f)
        except Exception as e:
            _log_event({"event": "list_all_sessions_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to read JSON: {e}")
            return []
    elif db_file.suffix == ".csv":
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row["metadata"] = json.loads(row.get("metadata", "{}"))
                    except Exception:
                        pass
                    sessions.append(row)
        except Exception as e:
            _log_event({"event": "list_all_sessions_failed", "error": str(e)})
            print(f"{TEXT_INDICATORS['error']} Failed to read CSV: {e}")
            return []
    else:
        print(f"{TEXT_INDICATORS['error']} Unsupported session storage format: {db_file}")
        _log_event({"event": "list_all_sessions_failed", "error": "unsupported format"})
        return []
    return sessions


# Example entrypoint for CLI usage
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified Session Management System")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--discover-active", action="store_true", help="Discover all active sessions")
    parser.add_argument("--get", type=str, default=None, help="Get session by ID")
    parser.add_argument("--input-db", type=str, required=True, help="Path to session storage file")
    parser.add_argument("--output-db", type=str, default=None, help="Destination SQLite DB for consolidation")
    parser.add_argument("--consolidate", action="store_true", help="Consolidate all sessions into output DB")
    parser.add_argument("--backup-dir", type=str, default=None, help="Backup directory for output DB")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output DB if exists")
    args = parser.parse_args()

    if args.list:
        sessions = list_all_sessions(args.input_db)
        print(json.dumps(sessions, indent=2))
    elif args.discover_active:
        sessions = discover_active_sessions(args.input_db)
        print(json.dumps(sessions, indent=2))
    elif args.get:
        session = get_session_by_id(args.input_db, args.get)
        print(json.dumps(session, indent=2))
    elif args.consolidate:
        sessions = list_all_sessions(args.input_db)
        if not args.output_db:
            print("[ERROR] --output-db required for consolidation.")
            exit(1)
        consolidate_sessions_atomic(sessions, args.output_db, overwrite=args.overwrite, backup_dir=args.backup_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()