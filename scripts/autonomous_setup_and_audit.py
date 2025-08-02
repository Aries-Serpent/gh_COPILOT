"""Enterprise automation script skeleton for setup and auditing."""

from __future__ import annotations

import logging
import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from secondary_copilot_validator import SecondaryCopilotValidator
from scripts.code_placeholder_audit import main as placeholder_audit
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from template_engine.template_synchronizer import _compliance_score
from utils.log_utils import _log_event, TABLE_SCHEMAS
from utils.lessons_learned_integrator import load_lessons, apply_lessons


LOGGER = logging.getLogger(__name__)


def init_database(db_path: Path) -> None:
    """Create database if it does not exist."""
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.close()
        LOGGER.info("Created database %s", db_path)


def load_lesson_dataset(db_path: Path) -> list[dict[str, str]]:
    """Load lessons from the database and log their application.

    Parameters
    ----------
    db_path:
        Path to the SQLite database containing the ``enhanced_lessons_learned``
        table.
    """
    lessons = load_lessons(db_path)
    apply_lessons(LOGGER, lessons)
    return lessons


def ingest_assets(doc_path: Path, template_path: Path, db_path: Path) -> None:
    """Load documentation and template assets into ``db_path``.

    Files with ``.md``, ``.txt``, ``.json``, and ``.sql`` extensions are
    collected. Line endings are normalized and trailing whitespace stripped
    before hashing.

    This replicates the behavior of :mod:`documentation_ingestor` and
    :mod:`template_asset_ingestor` but targets ``production.db`` instead of
    ``enterprise_assets.db``.
    """
    LOGGER.info("Ingesting assets from %s and %s", doc_path, template_path)

    from datetime import datetime, timezone

    from scripts.database.cross_database_sync_logger import log_sync_operation

    # Gather files
    extensions = [".md", ".txt", ".json", ".sql"]
    doc_files = [p for p in doc_path.rglob("*") if p.is_file() and p.suffix in extensions] if doc_path.exists() else []
    tmpl_files = (
        [p for p in template_path.rglob("*") if p.is_file() and p.suffix in extensions]
        if template_path.exists()
        else []
    )

    analytics_db = Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "databases" / "analytics.db"
    _log_event({"event": "ingestion_start"}, table="correction_logs", db_path=analytics_db)
    # Resolve user once for audit trail entries
    user = os.getenv("USER", "system")
    conn = sqlite3.connect(db_path)
    audit_conn = sqlite3.connect(analytics_db)
    audit_conn.executescript(
        TABLE_SCHEMAS["corrections"]
        + TABLE_SCHEMAS["correction_history"]
        + TABLE_SCHEMAS["code_audit_history"]
        + TABLE_SCHEMAS["violation_logs"]
    )
    try:
        # Ensure required tables exist
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documentation_assets ("
            "id INTEGER PRIMARY KEY,"
            "doc_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL,"
            "modified_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS template_assets ("
            "id INTEGER PRIMARY KEY,"
            "template_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pattern_assets ("
            "id INTEGER PRIMARY KEY,"
            "pattern TEXT NOT NULL,"
            "usage_count INTEGER DEFAULT 0,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS corrections ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "file_path TEXT,"
            "rationale TEXT,"
            "compliance_score REAL,"
            "rollback_reference TEXT,"
            "ts TEXT"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS code_audit_history ("
            "id INTEGER PRIMARY KEY,"
            "audit_entry TEXT NOT NULL,"
            "user TEXT NOT NULL,"
            "timestamp TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS correction_history ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "session_id TEXT NOT NULL,"
            "file_path TEXT NOT NULL,"
            "action TEXT NOT NULL,"
            "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "details TEXT"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS violation_logs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "timestamp TEXT NOT NULL,"
            "event TEXT,"
            "details TEXT NOT NULL,"
            "count INTEGER"
            ")"
        )

        start_docs = datetime.now(timezone.utc)
        with tqdm(total=len(doc_files), desc="Docs", unit="file") as bar:
            conn.execute("BEGIN")
            session_id = f"INGEST_DOCS_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            for path in doc_files:
                if path.stat().st_size == 0:
                    bar.update(1)
                    continue
                raw = path.read_text(encoding="utf-8")
                content = "\n".join(line.rstrip() for line in raw.splitlines())
                digest = hashlib.sha256(content.encode()).hexdigest()
                modified_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
                conn.execute(
                    "INSERT INTO documentation_assets (doc_path, content_hash, created_at, modified_at)"
                    " VALUES (?, ?, ?, ?)",
                    (
                        str(path.relative_to(doc_path.parent)),
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                        modified_at,
                    ),
                )
                score = _compliance_score(content)
                conn.execute(
                    "INSERT INTO corrections (file_path, rationale, compliance_score, rollback_reference, ts)"
                    " VALUES (?, ?, ?, NULL, ?)",
                    (
                        str(path.relative_to(doc_path.parent)),
                        "Asset ingested",
                        score,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO code_audit_history (audit_entry, user, timestamp) VALUES (?, ?, ?)",
                    (
                        f"ingested:{path.name}",
                        user,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO correction_history (user_id, session_id, file_path, action, timestamp)"
                    " VALUES (?, ?, ?, 'ingested', ?)",
                    (
                        0,
                        session_id,
                        str(path.relative_to(doc_path.parent)),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                _log_event(
                    {
                        "event": "asset_ingested",
                        "asset_type": "documentation",
                        "path": str(path.relative_to(doc_path.parent)),
                        "compliance_score": score,
                    },
                    table="correction_logs",
                    db_path=analytics_db,
                    test_mode=False,
                )
                audit_conn.execute(
                    "INSERT INTO corrections (file_path, rationale, compliance_score, ts) VALUES (?, 'ingest', ?, ?)",
                    (
                        str(path.relative_to(doc_path.parent)),
                        score,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                audit_conn.execute(
                    "INSERT INTO correction_history (user_id, session_id, file_path, action, timestamp, details) VALUES (1, 'ingest_assets', ?, 'ingest', ?, ?)",
                    (
                        str(path.relative_to(doc_path.parent)),
                        datetime.now(timezone.utc).isoformat(),
                        "",
                    ),
                )
                audit_conn.execute(
                    "INSERT INTO code_audit_history (audit_entry, user, timestamp) VALUES (?, ?, ?)",
                    ("documentation_ingest", user, datetime.now(timezone.utc).isoformat()),
                )
                bar.update(1)
            conn.commit()
        log_sync_operation(db_path, "documentation_ingestion", start_time=start_docs)

        start_tmpl = datetime.now(timezone.utc)
        with tqdm(total=len(tmpl_files), desc="Templates", unit="file") as bar:
            conn.execute("BEGIN")
            session_id_t = f"INGEST_TMPL_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            for path in tmpl_files:
                raw = path.read_text(encoding="utf-8")
                content = "\n".join(line.rstrip() for line in raw.splitlines())
                digest = hashlib.sha256(content.encode()).hexdigest()
                conn.execute(
                    "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
                    (
                        str(path.relative_to(template_path.parent)),
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO pattern_assets (pattern, usage_count, created_at) VALUES (?, 0, ?)",
                    (content[:1000], datetime.now(timezone.utc).isoformat()),
                )
                score = _compliance_score(content)
                conn.execute(
                    "INSERT INTO corrections (file_path, rationale, compliance_score, rollback_reference, ts)"
                    " VALUES (?, ?, ?, NULL, ?)",
                    (
                        str(path.relative_to(template_path.parent)),
                        "Asset ingested",
                        score,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO code_audit_history (audit_entry, user, timestamp) VALUES (?, ?, ?)",
                    (
                        f"ingested:{path.name}",
                        user,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO correction_history (user_id, session_id, file_path, action, timestamp)"
                    " VALUES (?, ?, ?, 'ingested', ?)",
                    (
                        0,
                        session_id_t,
                        str(path.relative_to(template_path.parent)),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                _log_event(
                    {
                        "event": "asset_ingested",
                        "asset_type": "template",
                        "path": str(path.relative_to(template_path.parent)),
                        "compliance_score": score,
                    },
                    table="correction_logs",
                    db_path=analytics_db,
                    test_mode=False,
                )
                audit_conn.execute(
                    "INSERT INTO corrections (file_path, rationale, compliance_score, ts) VALUES (?, 'ingest', ?, ?)",
                    (
                        str(path.relative_to(template_path.parent)),
                        score,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                audit_conn.execute(
                    "INSERT INTO correction_history (user_id, session_id, file_path, action, timestamp) VALUES (1, 'ingest_assets', ?, 'ingest', ?, ?)",
                    (
                        str(path.relative_to(template_path.parent)),
                        datetime.now(timezone.utc).isoformat(),
                        "",
                    ),
                )
                audit_conn.execute(
                    "INSERT INTO code_audit_history (audit_entry, user, timestamp) VALUES (?, ?, ?)",
                    ("template_ingest", user, datetime.now(timezone.utc).isoformat()),
                )
                bar.update(1)
            conn.commit()
        log_sync_operation(db_path, "template_ingestion", start_time=start_tmpl)
        from scripts.database.ingestion_validator import IngestionValidator

        validator = IngestionValidator(doc_path.parent, db_path, analytics_db)
        if not validator.validate():
            raise RuntimeError("Asset ingestion validation failed")
    except Exception as exc:
        conn.rollback()
        audit_conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
            (datetime.now(timezone.utc).isoformat(), str(exc)),
        )
        _log_event({"event": "ingestion_rollback"}, table="rollback_logs", db_path=analytics_db)
        _log_event({"event": "ingestion_failed", "details": str(exc)}, table="violation_logs", db_path=analytics_db)
        raise
    finally:
        conn.close()
        audit_conn.commit()
        audit_conn.close()
        _log_event({"event": "ingestion_complete"}, table="correction_logs", db_path=analytics_db)


def run_audit(workspace: Path, analytics_db: Path, production_db: Optional[Path], dashboard_dir: Path) -> None:
    """Run placeholder audit with visual progress."""
    LOGGER.info("Starting placeholder audit")
    _log_event({"event": "audit_start"}, table="correction_logs", db_path=analytics_db)
    try:
        placeholder_audit(
            workspace_path=str(workspace),
            analytics_db=str(analytics_db),
            production_db=str(production_db) if production_db else None,
            dashboard_dir=str(dashboard_dir),
        )
    except Exception:
        CorrectionLoggerRollback(analytics_db).auto_rollback(dashboard_dir / "placeholder_summary.json", None)
        _log_event({"event": "audit_failed"}, table="violation_logs", db_path=analytics_db)
        raise
    finally:
        _log_event({"event": "audit_complete"}, table="correction_logs", db_path=analytics_db)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    analytics_db = workspace / "databases" / "analytics.db"
    production_db = workspace / "databases" / "production.db"
    dashboard_dir = workspace / "dashboard" / "compliance"

    init_database(analytics_db)
    init_database(production_db)

    lessons = load_lesson_dataset(production_db)
    _log_event(
        {"event": "lessons_loaded", "count": len(lessons)},
        table="correction_logs",
        db_path=analytics_db,
    )

    ingest_assets(workspace / "documentation", workspace / "template_engine", production_db)

    run_audit(workspace, analytics_db, production_db, dashboard_dir)

    validator = SecondaryCopilotValidator()
    valid = validator.validate_corrections([__file__])
    _log_event({"event": "secondary_validation", "result": valid}, table="correction_logs", db_path=analytics_db)

    LOGGER.info("Automation complete")


if __name__ == "__main__":
    main()
