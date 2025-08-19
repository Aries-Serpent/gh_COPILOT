#!/usr/bin/env python3
"""Ingest Markdown files into ``documentation_assets`` table."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from enterprise_modules.compliance import (
    enforce_anti_recursion,
    validate_enterprise_operation,
)

# ``pid_recursion_guard`` may not be available in lightweight environments.
try:  # pragma: no cover - optional import
    from enterprise_modules.compliance import pid_recursion_guard  # type: ignore
    _PID_GUARD_AVAILABLE = True
except Exception:  # pragma: no cover - fallback to no-op decorator
    _PID_GUARD_AVAILABLE = False

    def pid_recursion_guard(func):  # type: ignore
        return func

from template_engine.learning_templates import get_dataset_sources
from secondary_copilot_validator import SecondaryCopilotValidator
from utils.log_utils import log_event
from tqdm import tqdm

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.ingestion_utils import AssetIngestor, IngestorConfig
from scripts.database.size_compliance_checker import check_database_sizes
from scripts.database.schema_validators import ensure_documentation_schema
from scripts.database.unified_database_initializer import initialize_database

__all__ = ["ingest_documentation", "pid_recursion_guard", "_PID_GUARD_AVAILABLE"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_RECURSION_CTX = SimpleNamespace()


@pid_recursion_guard
def ingest_documentation(
    workspace: Path,
    docs_dir: Path | None = None,
    timeout_seconds: int | None = None,  # pragma: no cover - retained for API compatibility
    *,
    retain_history: bool = True,
) -> None:
    """Ingest Markdown files into ``enterprise_assets.db``."""

    if not validate_enterprise_operation():
        raise RuntimeError("Enterprise operation validation failed")
    enforce_anti_recursion(_RECURSION_CTX)

    validator = SecondaryCopilotValidator()

    db_dir = workspace / "databases"
    analytics_db = Path(os.getenv("ANALYTICS_DB", str(db_dir / "analytics.db")))
    analytics_db.parent.mkdir(parents=True, exist_ok=True)

    db_path = db_dir / "enterprise_assets.db"
    if not db_path.exists():
        initialize_database(db_path)
    ensure_documentation_schema(db_path)

    docs_dir = docs_dir or (workspace / "documentation")
    dataset_dbs = get_dataset_sources(str(workspace))

    ingestor = AssetIngestor(
        workspace,
        IngestorConfig(
            table="documentation_assets",
            path_column="doc_path",
            patterns=["*.md"],
        ),
    )

    start_time = datetime.now(timezone.utc)
    results = ingestor.ingest(
        docs_dir,
        dataset_dbs=dataset_dbs,
        retain_history=retain_history,
        extra_columns={
            "modified_at": lambda p: datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
        },
    )

    for res in tqdm(results, desc="Docs", unit="file"):
        file_start = datetime.now(timezone.utc)
        log_sync_operation(
            ingestor.db_path,
            "documentation_ingestion",
            status=res.status,
            start_time=file_start,
        )
        log_event(
            {
                "module": "documentation_ingestor",
                "level": "INFO",
                "doc_path": res.path,
                "status": res.status,
                "sha256": res.sha256,
                "md5": res.md5,
            },
            db_path=analytics_db,
        )
        if res.status != "DUPLICATE":
            validator.validate_corrections([str(workspace / res.path)])

    log_sync_operation(ingestor.db_path, "documentation_ingestion", start_time=start_time)

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
        _RECURSION_CTX.recursion_depth -= 1
        ancestors = getattr(_RECURSION_CTX, "ancestors", [])
        if ancestors:
            ancestors.pop()

