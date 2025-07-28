import argparse
from pathlib import Path
from typing import Optional

from scripts.database.documentation_ingestor import ingest_documentation
from scripts.database.template_asset_ingestor import ingest_templates
from scripts.code_placeholder_audit import main as run_audit


def init_databases(workspace: Path) -> None:
    """Create key databases if they don't exist."""
    db_dir = workspace / "databases"
    db_dir.mkdir(exist_ok=True)
    for name in ["production.db", "analytics.db"]:
        db_path = db_dir / name
        if not db_path.exists():
            db_path.touch()


def run_setup(workspace: Path, docs: Optional[Path], templates: Optional[Path]) -> None:
    init_databases(workspace)
    if docs:
        ingest_documentation(workspace, docs)
    if templates:
        ingest_templates(workspace, templates)
    run_audit(
        workspace_path=str(workspace),
        analytics_db=str(workspace / "databases" / "analytics.db"),
        production_db=str(workspace / "databases" / "production.db"),
        dashboard_dir=str(workspace / "dashboard" / "compliance"),
        timeout_minutes=30,
        simulate=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize databases and audit workspace")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--docs", type=Path)
    parser.add_argument("--templates", type=Path)
    args = parser.parse_args()
    run_setup(args.workspace, args.docs, args.templates)
