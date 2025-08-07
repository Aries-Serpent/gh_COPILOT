from __future__ import annotations

"""Deploy the web GUI to the production environment.

This script reflects the new ``web_gui`` directory layout at the repository
root.
"""

from pathlib import Path
import os

from .environment_migration import migrate_environment
from .backup_manager import create_backup
from .data_migration import migrate_data

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"


def deploy_to_production() -> None:
    """Simulate deployment of the web GUI to the production environment."""
    migrate_environment(["production"])
    migrate_data("analytics", "production")
    create_backup("production")
    print(f"Deploying web GUI from {WEB_GUI_PATH} to production environment")


if __name__ == "__main__":
    deploy_to_production()
