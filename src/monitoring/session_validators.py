from __future__ import annotations

"""Validators for session shutdown integrity.

This module provides simple checks used during shutdown of a session to
ensure the environment is left in a clean state.  It currently validates
that no file handles remain open within a given workspace and that the
session log indicates a graceful shutdown.
"""

from pathlib import Path
from typing import List

try:  # pragma: no cover - psutil is optional at runtime
    import psutil
except Exception:  # pragma: no cover - keep fallback simple
    psutil = None  # type: ignore[assignment]
    import gc
    import io


def find_open_handles(root: Path | None = None) -> List[str]:
    """Return a list of open file paths under ``root``.

    Parameters
    ----------
    root:
        Optional directory used to filter results. Only file handles whose
        path is located inside this directory are returned. When ``None``
        all open file handles for the current process are reported.
    """

    handles: List[str] = []

    if psutil is not None:
        process = psutil.Process()
        for info in process.open_files():
            try:
                path = Path(info.path)
            except OSError:
                continue
            if root is None or root in path.parents or path == root:
                handles.append(str(path))
        return handles

    # Fallback: inspect live file objects via the garbage collector.
    for obj in gc.get_objects():  # pragma: no cover - simple fallback
        if isinstance(obj, io.IOBase) and not obj.closed:
            try:
                path = Path(obj.name)
            except Exception:
                continue
            if root is None or root in path.parents or path == root:
                handles.append(str(path))
    return handles


def log_is_complete(log_path: Path) -> bool:
    """Return ``True`` if ``log_path`` contains a completion marker.

    A session log is considered complete when the file exists and its last
    non-empty line equals ``"SHUTDOWN COMPLETE"``.
    """

    try:
        content = log_path.read_text().strip().splitlines()
    except FileNotFoundError:
        return False
    return bool(content) and content[-1] == "SHUTDOWN COMPLETE"


def validate_session(log_path: Path) -> List[str]:
    """Run all session validators and return a list of error messages."""

    errors: List[str] = []

    open_handles = find_open_handles(log_path.parent)
    if open_handles:
        errors.append(f"open handles detected: {open_handles}")

    if not log_is_complete(log_path):
        errors.append("incomplete log detected")

    return errors


__all__ = [
    "find_open_handles",
    "log_is_complete",
    "validate_session",
]
