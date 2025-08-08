"""Codex logging utilities for gh_COPILOT Enterprise Toolkit"""

from datetime import UTC, datetime
from pathlib import Path

from enterprise_modules.database_utils import (
    enterprise_database_context,
    execute_safe_insert,
    execute_safe_query,
)
from enterprise_modules.compliance import (
    ComplianceError,
    validate_enterprise_operation,
)

CODEX_LOG_DB = Path("databases") / "codex_session_logs.db"


def log_codex_action(
    session_id: str,
    action: str,
    statement: str,
    *,
    db_path: Path = CODEX_LOG_DB,
) -> bool:
    """Record a Codex action in the codex log database with compliance checks."""
    if not validate_enterprise_operation(str(db_path)):
        raise ComplianceError(f"Forbidden database write: {db_path}")

    timestamp = datetime.now(UTC).isoformat()
    with enterprise_database_context(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_log (
                session_id TEXT,
                action TEXT,
                statement TEXT,
                timestamp TEXT
            )
            """
        )
        data = {
            "session_id": session_id,
            "action": action,
            "statement": statement,
            "timestamp": timestamp,
        }
        return execute_safe_insert(conn, "codex_log", data)


def get_codex_history(
    session_id: str,
    *,
    db_path: Path = CODEX_LOG_DB,
) -> list:
    """Retrieve Codex actions for ``session_id`` ordered by timestamp."""
    with enterprise_database_context(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_log (
                session_id TEXT,
                action TEXT,
                statement TEXT,
                timestamp TEXT
            )
            """
        )
        rows = execute_safe_query(
            conn,
            "SELECT action, statement, timestamp FROM codex_log WHERE session_id=? ORDER BY timestamp",
            (session_id,),
        )
        return [dict(r) for r in rows] if rows else []
