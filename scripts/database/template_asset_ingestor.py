"""Ingest templates and patterns into enterprise_assets.db."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from enterprise_modules.compliance import (
    pid_recursion_guard,
    validate_enterprise_operation,
)
from template_engine.learning_templates import (
    get_dataset_sources,
    get_lesson_templates,
)
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator
from utils.log_utils import log_event
from tqdm import tqdm

from .cross_database_sync_logger import log_sync_operation
from .ingestion_utils import AssetIngestor, IngestorConfig
from .size_compliance_checker import check_database_sizes
from .schema_validators import ensure_template_schema
from .unified_database_initializer import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BUSY_TIMEOUT_MS = 30_000


@pid_recursion_guard
def ingest_templates(workspace: Path, template_dir: Path | None = None) -> None:
    """Load template and pattern data into ``enterprise_assets.db``."""

    validate_enterprise_operation()

    db_dir = workspace / "databases"
    analytics_db = db_dir / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)

    db_path = db_dir / "enterprise_assets.db"
    if not db_path.exists():
        initialize_database(db_path)
    ensure_template_schema(db_path)

    template_dir = template_dir or (workspace / "prompts")
    dataset_dbs = get_dataset_sources(str(workspace))

    ingestor = AssetIngestor(
        workspace,
        IngestorConfig(
            table="template_assets",
            path_column="template_path",
            patterns=["*.md"],
        ),
    )

    start_time = datetime.now(timezone.utc)
    results = ingestor.ingest(template_dir, dataset_dbs=dataset_dbs)

    new_count = 0
    dup_count = 0
    for res in tqdm(results, desc="Templates", unit="file"):
        file_start = datetime.now(timezone.utc)
        log_sync_operation(
            ingestor.db_path,
            "template_ingestion",
            status=res.status,
            start_time=file_start,
        )
        if res.status == "DUPLICATE":
            dup_count += 1
        else:
            new_count += 1
        log_event(
            {
                "module": "template_ingestor",
                "level": "INFO",
                "template_path": res.path,
                "status": res.status,
                "sha256": res.sha256,
            },
            db_path=analytics_db,
        )

    log_sync_operation(ingestor.db_path, "template_ingestion", start_time=start_time)

    # Insert lesson templates into pattern_assets table
    with sqlite3.connect(ingestor.db_path) as conn:
        lesson_templates = get_lesson_templates()
        existing_lessons = {
            row[0]
            for row in conn.execute(
                "SELECT lesson_name FROM pattern_assets WHERE lesson_name IS NOT NULL"
            )
        }
        for name, content in lesson_templates.items():
            if name in existing_lessons:
                continue
            conn.execute(
                (
                    "INSERT INTO pattern_assets (pattern, usage_count, lesson_name, created_at) "
                    "VALUES (?, 0, ?, ?)"
                ),
                (content[:1000], name, datetime.now(timezone.utc).isoformat()),
            )
        conn.commit()

    summary = {
        "description": "template_dedup_summary",
        "details": json.dumps(
            {"db_path": str(ingestor.db_path), "new": new_count, "duplicates": dup_count}
        ),
    }
    log_event(summary, db_path=analytics_db)
    logger.info(json.dumps({"event": "template_dedup_summary", **json.loads(summary["details"]) }))

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    orchestrator = DualCopilotOrchestrator()
    orchestrator.validator.validate_corrections([str(ingestor.db_path)])

