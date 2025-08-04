from __future__ import annotations
import logging
import os
import psutil

class AntiRecursionEnforcer:
    """Detect and handle recursive session execution."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def enforce_no_recursion(self, current_pid: int | None = None) -> None:
        """Terminate the session if recursion is detected.

        If ``current_pid`` is not found in the process table, a warning is
        logged and the check is skipped to avoid crashes during integration
        tests where the PID might be stale.
        """
        pid = current_pid or os.getpid()
        if not psutil.pid_exists(pid):
            self.logger.warning(
                "PID %s not found in process table; skipping recursion enforcement",
                pid,
            )
            return
        if self._detect_recursion(pid):
            self.logger.critical("Recursion detected in session %s. Aborting.", pid)
            self._terminate_session(pid)

    def _detect_recursion(self, pid: int) -> bool:
        """Return ``True`` if another process shares the same command line."""
        try:
            cmdline = psutil.Process(pid).cmdline()
        except psutil.Error:
            return False
        for proc in psutil.process_iter(["pid", "cmdline"]):
            if proc.info["pid"] == pid:
                continue
            if proc.info.get("cmdline") == cmdline:
                return True
        return False

    def _terminate_session(self, pid: int) -> None:
        """Attempt to terminate the session associated with ``pid``."""
        try:
            psutil.Process(pid).terminate()
        except psutil.Error as exc:  # pragma: no cover - best effort
            self.logger.error("Failed to terminate session %s: %s", pid, exc)
