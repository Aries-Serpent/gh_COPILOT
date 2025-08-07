from __future__ import annotations

"""Deploy quantum modules alongside the web GUI.

This helper locates both the ``web_gui`` and ``quantum`` directories using the
updated repository layout and reports the simulated deployment actions.
It relies on validated migrations and dedicated quantum backups.
"""

from pathlib import Path
import os

from .environment_migration import migrate_environment
from .quantum_backup import backup_quantum

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"
QUANTUM_MODULE_PATH = WORKSPACE / "quantum"


def deploy_quantum_modules() -> None:
    """Simulate deployment of quantum modules into the web GUI."""
    migrate_environment(["quantum"])
    backup_quantum()
    print(
        f"Deploying quantum modules from {QUANTUM_MODULE_PATH} "
        f"to web GUI at {WEB_GUI_PATH}"
    )


if __name__ == "__main__":
    deploy_quantum_modules()
