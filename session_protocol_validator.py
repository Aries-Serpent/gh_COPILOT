#!/usr/bin/env python3
"""Session Protocol Validator
=============================

Validates session startup and shutdown protocols for the
`UnifiedSessionManagementSystem`. The validator performs
zero-byte file checks to ensure workspace integrity before
sessions are started or completed.
"""

from pathlib import Path
from typing import List, Optional
import logging

from copilot.common import get_workspace_path


class SessionProtocolValidator:
    """Enforce basic session startup and shutdown rules."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = get_workspace_path(workspace_root)
        self.logger = logging.getLogger(__name__)

    # internal helper -----------------------------------------------------
    def _scan_zero_byte_files(self) -> List[Path]:
        zero_byte_files = []
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size == 0:
                zero_byte_files.append(file_path)
        return zero_byte_files

    # public API ----------------------------------------------------------
    def validate_startup(self) -> bool:
        """Validate startup protocol.

        Returns ``True`` if no zero-byte files are detected.
        """
        self.logger.info("Validating session startup protocol")
        zero_byte_files = self._scan_zero_byte_files()
        if zero_byte_files:
            for f in zero_byte_files:
                self.logger.error(f"Zero-byte file detected: {f}")
            return False
        return True

    def validate_shutdown(self) -> bool:
        """Validate shutdown protocol.

        Returns ``True`` if no zero-byte files are detected.
        """
        self.logger.info("Validating session shutdown protocol")
        zero_byte_files = self._scan_zero_byte_files()
        if zero_byte_files:
            for f in zero_byte_files:
                self.logger.error(f"Zero-byte file detected before shutdown: {f}")
            return False
        return True
