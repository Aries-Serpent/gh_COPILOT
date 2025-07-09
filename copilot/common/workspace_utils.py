from pathlib import Path
import os
from typing import Optional

DEFAULT_ENV_VAR = "GH_COPILOT_WORKSPACE"
DEFAULT_PATH = Path("e:/gh_COPILOT")


def get_workspace_path(workspace: Optional[str] = None) -> Path:
    """Return a workspace path from a parameter or environment variable."""
    if workspace:
        return Path(workspace)
    return Path(os.getenv(DEFAULT_ENV_VAR, DEFAULT_PATH))
