#!/usr/bin/env python3
"""Utilities for resolving the workspace path."""

import os
from pathlib import Path
from typing import Optional

DEFAULT_ENV_VAR = "GH_COPILOT_WORKSPACE"


def get_workspace_path(workspace: Optional[str] = None) -> Path:
    """Return a workspace path from a parameter or environment variable.

    When ``workspace`` is provided its value is used directly. Otherwise the
    ``GH_COPILOT_WORKSPACE`` environment variable is consulted. If that is not
    set, ``Path.cwd()`` is returned.
    """

    if workspace:
        return Path(workspace)

    env_path = os.getenv(DEFAULT_ENV_VAR)
    if env_path:
        return Path(env_path)

    return Path.cwd()


def _within_workspace(path: Path, workspace_root: Path) -> bool:
    """Return ``True`` if ``path`` is inside ``workspace_root``.

    Parameters
    ----------
    path:
        The path to check.
    workspace_root:
        The workspace root directory.

    Returns
    -------
    bool
        ``True`` if ``path`` resolves within ``workspace_root``.
    """

    try:
        path.resolve().relative_to(workspace_root)
        return True
    except ValueError:
        return False
