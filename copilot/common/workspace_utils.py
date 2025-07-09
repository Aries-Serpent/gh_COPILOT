import os
from pathlib import Path
from typing import Optional

DEFAULT_ENV_VAR = "GH_COPILOT_WORKSPACE"
DEFAULT_PATH = Path("/path/to/workspace")


def get_workspace_path(workspace: Optional[str] = None) -> Path:
    """Return a workspace path from a parameter or environment variable."""
    if workspace:
        return Path(workspace)
    return Path(os.getenv(DEFAULT_ENV_VAR, DEFAULT_PATH))
