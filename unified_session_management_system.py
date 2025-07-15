<<<<<<< HEAD
"""Command line wrapper for unified session management."""

from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable
import logging
import sqlite3
from datetime import datetime

from utils.validation_utils import detect_zero_byte_files
from scripts.session.anti_recursion_enforcer import anti_recursion_guard
from enterprise_modules.compliance import validate_environment, ComplianceError
from utils.logging_utils import ANALYTICS_DB

logger = logging.getLogger(__name__)

__all__ = [
    "ensure_no_zero_byte_files",
    "finalize_session",
    "prevent_recursion",
    "main",
]


def _record_zero_byte_findings(paths: list[Path], phase: str, session_id: str) -> None:
    """Persist zero-byte scan results to ``analytics.db``."""
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS zero_byte_files (
                path TEXT NOT NULL,
                phase TEXT NOT NULL,
                session_id TEXT NOT NULL,
                ts   TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO zero_byte_files (path, phase, session_id, ts) VALUES (?, ?, ?, ?)",
            [(str(p), phase, session_id, timestamp) for p in paths] or [],
        )


@contextmanager
def ensure_no_zero_byte_files(root: str | Path, session_id: str) -> None:
    """Verify the workspace is free of zero-byte files before and after the block."""
    root_path = Path(root)
    before = detect_zero_byte_files(root_path)
    _record_zero_byte_findings(before, "before", session_id)
    if before:
        for path in before:
            path.unlink(missing_ok=True)
        raise RuntimeError(f"Zero-byte files detected: {before}")
    yield
    after = detect_zero_byte_files(root_path)
    _record_zero_byte_findings(after, "after", session_id)
    if after:
        for path in after:
            path.unlink(missing_ok=True)
        raise RuntimeError(f"Zero-byte files detected: {after}")


def prevent_recursion(func: Callable) -> Callable:
    """Decorator forwarding to :func:`anti_recursion_guard`.

    It raises ``RuntimeError`` when ``func`` is invoked recursively within the
    same process. This lightweight wrapper is re-exported for convenience so
    other modules can apply the guard without importing validation utilities
    directly.
    """

    return anti_recursion_guard(func)


@prevent_recursion
def finalize_session(
    log_dir: str | Path,
    root: str | Path | None = None,
    session_id: str = "unknown",
) -> str:
    """Verify logs are complete and record a session integrity hash.

    A zero-byte file scan is executed before and after processing. Results are
    persisted to ``analytics.db`` using ``session_id`` for traceability.

    Parameters
    ----------
    log_dir:
        Directory containing session log files.
    root:
        Workspace root to scan for zero-byte files. Defaults to ``log_dir``'s
        parent directory.
    session_id:
        Identifier recorded alongside zero-byte findings.

    Returns
    -------
    str
        SHA256 hash of concatenated log contents.
    """

    root_path = Path(root) if root else Path(log_dir).parent
    with ensure_no_zero_byte_files(root_path, session_id):
        log_path = Path(log_dir)
        logs = sorted(p for p in log_path.glob("*.log") if p.is_file())
        if not logs:
            raise RuntimeError("No log files found for session")
        for entry in logs:
            if entry.stat().st_size == 0:
                raise RuntimeError(f"Empty log file detected: {entry}")

        digest = sha256()
        for entry in logs:
            digest.update(entry.read_bytes())
        hash_value = digest.hexdigest()

        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_hashes (
                    hash TEXT PRIMARY KEY,
                    ts   TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO session_hashes (hash, ts) VALUES (?, ?)",
                (hash_value, datetime.utcnow().isoformat()),
            )

    return hash_value

@anti_recursion_guard
def main() -> int:
    """Run session validation and return an exit code."""
    from scripts.utilities.unified_session_management_system import (
        UnifiedSessionManagementSystem,
    )
    try:
        validate_environment()
    except ComplianceError as exc:  # pragma: no cover - simple error log
        logger.error("Environment validation failed: %s", exc)
        print("Invalid")
        return 1

    system = UnifiedSessionManagementSystem()
    logger.info("Lifecycle start")
    success = False
    with ensure_no_zero_byte_files(system.workspace_root, system.session_id):
        success = system.start_session()
        system.end_session()
        finalize_session(
            Path(system.workspace_root) / "logs",
            system.workspace_root,
            system.session_id,
        )
    logger.info("Lifecycle end")
    print("Valid" if success else "Invalid")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
=======
#!/usr/bin/env python3
"""
UnifiedSessionManagementSystem - Enterprise Utility Script
Generated: 2025-07-10 18:10:24

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Visual processing indicators
"""


from copilot.common.workspace_utils import get_workspace_path

from session_protocol_validator import SessionProtocolValidator
import logging

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class UnifiedSessionManagementSystem:
    """Manage session start validation."""

    def __init__(self, workspace_root: str | None = None) -> None:
        self.workspace_root = get_workspace_path(workspace_root)
        self.validator = SessionProtocolValidator(str(self.workspace_root))

    def start_session(self) -> bool:
        """Return ``True`` if session validation succeeds."""
        return self.validator.validate_startup()


def main() -> None:
    system = UnifiedSessionManagementSystem()
    print("Valid" if system.start_session() else "Invalid")


if __name__ == "__main__":
    main()
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
