#!/usr/bin/env python3
"""Enterprise automation skeleton for setup, ingestion, and audit."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from scripts.database.unified_database_initializer import initialize_database
from scripts.database.documentation_ingestor import ingest_documentation
from scripts.database.template_asset_ingestor import ingest_templates
from scripts.code_placeholder_audit import main as run_audit


LOG = logging.getLogger(__name__)


def chunk_anti_recursion_validation() -> None:
    """Validate workspace and backup paths before file operations."""
    from enterprise_modules.compliance import validate_enterprise_operation

    validate_enterprise_operation()


def ensure_databases(workspace: Path) -> None:
    """Create required databases if they do not exist."""
    for name in ["production.db", "analytics.db", "enterprise_assets.db"]:
        db_path = workspace / "databases" / name
        if not db_path.exists():
            LOG.info("Initializing %s", db_path)
            initialize_database(db_path)


def ingest_assets(workspace: Path) -> None:
    """Ingest documentation and template assets."""
    docs = workspace / "documentation"
    templates = workspace / "prompts"
    ingest_documentation(workspace, docs)
    ingest_templates(workspace, templates)


def run_placeholder_audit(workspace: Path) -> None:
    """Run the placeholder audit script."""
    analytics = workspace / "databases" / "analytics.db"
    production = workspace / "databases" / "production.db"
    dashboard = workspace / "dashboard" / "compliance"
    run_audit(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(production),
        dashboard_dir=str(dashboard),
        timeout_minutes=30,
        simulate=False,
    )


def main() -> None:
    """Orchestrate setup, ingestion, and auditing."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    chunk_anti_recursion_validation()
    ensure_databases(workspace)
    ingest_assets(workspace)
    run_placeholder_audit(workspace)


if __name__ == "__main__":
    main()
