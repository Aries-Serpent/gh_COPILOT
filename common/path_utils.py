import os
from pathlib import Path


def get_workspace_root() -> Path:
    """Return the workspace root directory.

    The workspace root is determined by the ``GH_COPILOT_ROOT`` environment
    variable. If not set, the current working directory is used.
    """
    return Path(os.environ.get("GH_COPILOT_ROOT", os.getcwd())).resolve()
