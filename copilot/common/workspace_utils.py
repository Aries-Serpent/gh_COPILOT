"""Utilities for resolving the workspace path."""

from pathlib import Path
import os
from typing import Optional


DEFAULT_ENV_VAR = "GH_COPILOT_WORKSPACE"


def get_workspace_path(workspace: Optional[str] = None) -> Path:
    """Return a workspace path from a parameter or environment variable.

    When ``workspace`` is provided its value is used directly. Otherwise the
    ``GH_COPILOT_WORKSPACE`` environment variable is consulted. If that is not
    set, ``Path.home()`` is returned.
    """

    if workspace:
        return Path(workspace)

    env_path = os.getenv(DEFAULT_ENV_VAR)
    if env_path:
        return Path(env_path)

    return Path.home()
