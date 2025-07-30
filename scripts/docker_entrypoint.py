#!/usr/bin/env python3
"""Docker entrypoint for the enterprise dashboard."""

from utils.validation_utils import validate_enterprise_environment
from utils.cross_platform_paths import CrossPlatformPathManager
from dashboard.enterprise_dashboard import main
from scripts.database.unified_database_initializer import initialize_database


def _ensure_databases() -> None:
    """Initialize required databases when running inside Docker."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    db_path = workspace / "databases" / "enterprise_assets.db"
    if not db_path.exists():
        initialize_database(db_path)


if __name__ == "__main__":
    validate_enterprise_environment()
    _ensure_databases()
    main()
