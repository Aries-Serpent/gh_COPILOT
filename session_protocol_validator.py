#!/usr/bin/env python3
"""SessionProtocolValidator - Validates workspace for zero-byte files."""
import logging

from copilot.common.workspace_utils import get_workspace_path

TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class SessionProtocolValidator:
    """Check workspace integrity on startup."""

    def __init__(self, workspace_path: str | None = None) -> None:
        self.workspace_path = get_workspace_path(workspace_path)
        self.logger = logging.getLogger(__name__)

    def validate_startup(self) -> bool:
        """Return False if any zero-byte file is found."""
        self.logger.info(
            f"{TEXT_INDICATORS['start']} Validating {self.workspace_path}")
        for path in self.workspace_path.rglob('*'):
            if path.is_file() and path.stat().st_size == 0:
                self.logger.error(
                    f"{TEXT_INDICATORS['error']} Zero-byte file {path}")
                return False
        self.logger.info(f"{TEXT_INDICATORS['success']} Validation passed")
        return True
