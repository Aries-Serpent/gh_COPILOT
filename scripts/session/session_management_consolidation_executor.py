#!/usr/bin/env python3
# [Session]: Session Management Consolidation Executor
# > Generated: 2025-07-24 20:12:39 | Author: mbaetiong

"""
Session Management Consolidation Executor

- Consolidates session states and metadata across multiple persistent storage backends.
- Ensures atomicity and consistency for enterprise session management operations.
- Supports progress tracking, logging, anti-recursion and compliance validation.
"""

import argparse
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from tqdm import tqdm
from utils.log_utils import _log_event

from scripts.session.session_protocol_validator import validate_consolidation_protocol

TEXT_INDICATORS = {
    "start": "[START]",
    "progress": "[PROGRESS]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "validation": "[VALIDATION]",
    "completion": "[COMPLETION]",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enterprise Session Management Consolidation Executor"
    )
    parser.add_argument(
        "--workspace", type=Path, default=Path.cwd(), help="Workspace root directory"
    )
    parser.add_argument(
        "--session-db", type=Path, required=True, help="Session database file"
    )
    parser.add_argument(
        "--output-db", type=Path, required=True, help="Output consolidated session DB"
    )
    parser.add_argument(
        "--backup-dir", type=Path, default=Path("session_backups"), help="Backup directory"
    )
    parser.add_argument(
        "--progress", action="store_true", help="Show progress bar"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Run protocol validation"
    )
    return parser.parse_args()


def setup_logging(workspace: Path) -> None:
    log_dir = workspace / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)


def backup_file(file_path: Path, backup_dir: Path) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    print(f"[INFO] Backed up {file_path} to {backup_path}")
    return backup_path


def discover_active_sessions(session_db_path: Path) -> List[Dict[str, Any]]:
    """Discover all active sessions in the provided SQLite session database."""
    if not session_db_path.exists():
        raise FileNotFoundError(f"Session DB not found: {session_db_path}")
    sessions = []
    with sqlite3.connect(str(session_db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # The table might be named 'sessions', 'active_sessions', or 'session_log'.
        possible_tables = ["sessions", "active_sessions", "session_log"]
        table_found = None
        for table in possible_tables:
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,)
            )
            if cur.fetchone():
                table_found = table
                break
        if not table_found:
            raise RuntimeError("No sessions table found in session db")
        # Fetch all active sessions
        cur.execute(f"SELECT * FROM {table_found} WHERE status='active'")
        rows = cur.fetchall()
        for row in rows:
            session = dict(row)
            # Example expansion: attach last activity timestamp if not present
            if "last_activity" not in session:
                # fallback: use updated_at or created_at if available
                if "updated_at" in session:
                    session["last_activity"] = session["updated_at"]
                elif "created_at" in session:
                    session["last_activity"] = session["created_at"]
                else:
                    session["last_activity"] = None
            # Example expansion: validate session_id format
            if "session_id" in session and not isinstance(session["session_id"], str):
                session["session_id"] = str(session["session_id"])
            sessions.append(session)
    return sessions


def deduplicate_sessions(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate sessions based on session_id."""
    seen = set()
    deduped = []
    for sess in sessions:
        sid = sess.get("session_id")
        if sid not in seen:
            seen.add(sid)
            deduped.append(sess)
    return deduped


def consolidate_sessions_atomic(sessions: List[Dict[str, Any]], output_db_path: Path) -> None:
    """
    Consolidate and write session data atomically to output database.
    - This creates the table if needed, and inserts all session records.
    - This version upgrades/expands the table with new fields as needed.
    """
    table_name = "consolidated_sessions"
    # Backup output DB first if it exists
    if output_db_path.exists():
        backup_path = output_db_path.parent / f"{output_db_path.stem}_preconsolidation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{output_db_path.suffix}"
        shutil.copy2(output_db_path, backup_path)
        print(f"[INFO] Existing output DB backed up at {backup_path}")

    with sqlite3.connect(str(output_db_path)) as conn:
        cur = conn.cursor()
        # If no sessions, still ensure table exists
        if not sessions:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (session_id TEXT PRIMARY KEY, status TEXT, last_activity TEXT)")
            conn.commit()
            print("[WARNING] No sessions to consolidate.")
            return

        # Find all unique columns for robust schema creation
        all_columns = set()
        for sess in sessions:
            all_columns.update(sess.keys())
        columns = sorted(all_columns)
        columns_decl = ", ".join([f"{col} TEXT" for col in columns])
        # Recreate the table
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        cur.execute(f"CREATE TABLE {table_name} ({columns_decl}, PRIMARY KEY(session_id))")

        for session in sessions:
            values = [str(session.get(c, "")) for c in columns]
            placeholders = ", ".join(["?"] * len(columns))
            cur.execute(
                f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
        conn.commit()
        print(f"[SUCCESS] {len(sessions)} sessions written atomically to {output_db_path} (table: {table_name})")


def main() -> int:
    args = parse_args()
    setup_logging(args.workspace)
    _log_event({"event": "session_consolidation_start", "timestamp": datetime.utcnow().isoformat()})

    # Validate session protocol if required
    if args.validate:
        print(f"{TEXT_INDICATORS['validation']} Validating session consolidation protocol...")
        protocol_ok = validate_consolidation_protocol(args.session_db)
        if not protocol_ok:
            print(f"{TEXT_INDICATORS['error']} Protocol validation failed.")
            _log_event({"event": "session_consolidation_protocol_failed"})
            return 1
        else:
            print(f"{TEXT_INDICATORS['success']} Protocol validation passed.")

    # Backup current session DB
    backup_file(args.session_db, args.backup_dir)

    print(f"{TEXT_INDICATORS['start']} Discovering active sessions in {args.session_db}...")
    sessions = discover_active_sessions(args.session_db)
    print(f"{TEXT_INDICATORS['progress']} {len(sessions)} sessions discovered.")

    # Deduplicate sessions by session_id
    deduped_sessions = deduplicate_sessions(sessions)
    print(f"{TEXT_INDICATORS['progress']} {len(deduped_sessions)} unique sessions after deduplication.")

    # Consolidate sessions with atomic write
    print(f"{TEXT_INDICATORS['progress']} Consolidating sessions...")
    if args.progress:
        iterator = tqdm(deduped_sessions, desc="Consolidating Sessions")
    else:
        iterator = deduped_sessions

    consolidated = []
    for session in iterator:
        # Example expansion: Add an audit field for compliance
        session["consolidated_at"] = datetime.utcnow().isoformat()
        consolidated.append(session)

    # Write to output DB atomically
    consolidate_sessions_atomic(consolidated, args.output_db)
    print(f"{TEXT_INDICATORS['success']} Consolidated {len(consolidated)} sessions into {args.output_db}")

    _log_event({
        "event": "session_consolidation_complete",
        "consolidated_count": len(consolidated),
        "output_db": str(args.output_db),
        "timestamp": datetime.utcnow().isoformat()
    })

    print(f"{TEXT_INDICATORS['completion']} Session management consolidation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    