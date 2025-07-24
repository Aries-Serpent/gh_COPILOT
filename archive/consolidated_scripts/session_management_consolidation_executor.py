"""Archive wrapper for :mod:`scripts.utilities.unified_session_management_system`."""

from pathlib import Path


class EnterpriseUtility:
    """Minimal utility for tests."""

    def __init__(self, workspace_path: str) -> None:
        self.workspace_path = workspace_path

    def perform_utility_function(self) -> bool:
        """Return ``False`` if zero-byte files exist in workspace."""
        for path in Path(self.workspace_path).rglob("*"):
            if path.is_file() and path.stat().st_size == 0:
                return False
        return True

    def execute_utility(self) -> bool:
        return self.perform_utility_function()
