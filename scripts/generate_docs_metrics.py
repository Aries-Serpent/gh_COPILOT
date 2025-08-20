#!/usr/bin/env python3
"""Generate documentation metrics in README files."""

from __future__ import annotations

import argparse
import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from utils.log_utils import DEFAULT_ANALYTICS_DB, _log_event
from scripts.validation.secondary_copilot_validator import (
    SecondaryCopilotValidator,
    run_dual_copilot_validation,
)
from scripts import validate_docs_metrics

# The production database resides under ``databases/``. Using this path avoids
# accidental creation of an empty database when ``production.db`` does not exist
# at the repository root.
DB_PATH = ROOT / "databases" / "production.db"
README_PATHS = [
    ROOT / "README.md",
    ROOT / "documentation" / "generated" / "README.md",
    ROOT / "documentation" / "generated" / "SYSTEM_STATUS.md",
]
DATABASE_LIST = ROOT / "documentation" / "DATABASE_LIST.md"


def get_metrics(db_path: Path = DB_PATH) -> dict[str, int]:
    """Return metrics gathered from the specified database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM enterprise_script_tracking")
    scripts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM script_template_patterns")
    templates = cur.fetchone()[0]
    conn.close()
    with DATABASE_LIST.open() as f:
        databases = sum(1 for line in f if line.strip().startswith("- ") and line.strip().endswith(".db"))
    return {"scripts": scripts, "templates": templates, "databases": databases}


def update_file(path: Path, metrics: dict[str, int]) -> None:
    content = path.read_text()
    content = re.sub(
        r"(\*Generated from Enterprise Documentation Database on ).*?\*",
        lambda m: f"{m.group(1)}{datetime.now():%Y-%m-%d %H:%M:%S}*",
        content,
    )
    content = re.sub(
        r"(\*Generated on ).*?\*",
        lambda m: f"{m.group(1)}{datetime.now():%Y-%m-%d %H:%M:%S}*",
        content,
    )
    content = re.sub(
        r"(Script Validation[^0-9]*)([0-9,]+)",
        lambda m: f"{m.group(1)}{metrics['scripts']:,}",
        content,
    )
    content = re.sub(
        r"([0-9,]+\s*Synchronized Databases)",
        f"{metrics['databases']:,} Synchronized Databases",
        content,
    )
    content = re.sub(
        r"([0-9,]+\s*databases operational)",
        f"{metrics['databases']:,} databases operational",
        content,
    )
    path.write_text(content)


def main(argv: list[str] | None = None) -> None:
    """Entry point for command-line execution."""
    parser = argparse.ArgumentParser(description="Generate documentation metrics in README files.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Path to the production database",
    )
    parser.add_argument(
        "--analytics-db",
        type=Path,
        default=DEFAULT_ANALYTICS_DB,
        help="Path to analytics database",
    )
    args = parser.parse_args(argv)

    logger.info("gathering documentation metrics")
    metrics = get_metrics(args.db_path)
    _log_event({"event": "generate_docs_metrics", "metrics": metrics}, db_path=args.analytics_db)
    for path in README_PATHS:
        if path.exists():
            logger.info("updating %s", path)
            update_file(path, metrics)
    _log_event({"event": "generate_docs_metrics_complete"}, db_path=args.analytics_db)

    validator = SecondaryCopilotValidator()

    def _primary() -> bool:
        return validate_docs_metrics.validate(args.db_path)

    def _secondary() -> bool:
        files = [str(path) for path in README_PATHS if path.exists()]
        return validator.validate_corrections(files)

    run_dual_copilot_validation(_primary, _secondary)
    logger.info("documentation metrics generation complete")


if __name__ == "__main__":
    main()
