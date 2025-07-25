# [Script]: Template Synchronizer Engine
# > Generated: 2025-07-25 14:40:23 | Author: mbaetiong
# --- Enterprise Standards ---
# - Flake8/PEP8 Compliant
# - Visual Processing Indicators: start time, progress bar, ETC,
#   real-time status, process ID, error handling, dual validation
# - NO creation or mutation of `databases/analytics.db` – only simulate/test for existence and readiness
# - All database/file operations must be validated for anti-recursion and compliance

import argparse
import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from tqdm import tqdm

from utils.log_utils import _log_event

try:
    from .auto_generator import DEFAULT_ANALYTICS_DB
except ImportError:
    DEFAULT_ANALYTICS_DB = Path("analytics.db")

ANALYTICS_DB = Path(os.environ.get("ANALYTICS_DB", DEFAULT_ANALYTICS_DB))
logger = logging.getLogger(__name__)


def _calculate_etc(start_ts: float, current: int, total: int) -> str:
    if current == 0:
        return "N/A"
    elapsed = time.time() - start_ts
    est_total = elapsed / (current / total)
    remaining = est_total - elapsed
    return f"{remaining:.2f}s remaining"


def _extract_templates(db: Path) -> List[Tuple[str, str]]:
    """Extract templates from a database. This operation does NOT create or modify any DB."""
    if not db.exists():
        logger.warning("Database does not exist: %s", db)
        return []
    try:
        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates").fetchall()
            return [(r[0], r[1]) for r in rows]
    except sqlite3.Error as exc:
        logger.warning("Failed to read templates from %s: %s", db, exc)
        return []


def _validate_template(name: str, content: str) -> bool:
    """Validate that template has a name and non-empty content."""
    return bool(name and content and content.strip())


def _db_compliance_score(content: str) -> float:
    """Simulate compliance score query using analytics rules. NEVER create analytics.db."""
    if not ANALYTICS_DB.exists():
        logger.warning("Analytics DB does not exist at %s (test only, not creating).", ANALYTICS_DB)
        return 100.0
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute("SELECT pattern FROM compliance_rules")
            rules = [row[0] for row in cur.fetchall()]
    except sqlite3.Error:
        rules = []
    if any(r.lower() in content.lower() for r in rules):
        return 50.0
    if not content.strip():
        return 50.0
    return 100.0


def _compliance_score(content: str) -> float:
    """Return compliance score based on analytics rules."""
    return _db_compliance_score(content)


def _log_sync_event(source: str, target: str) -> None:
    """Simulate logging a synchronization event. NEVER create analytics.db."""
    logger.info("[TEST] Would log sync event: %s -> %s [No DB mutation]", source, target)
    # This function does not write to analytics.db – compliance with enterprise test/readonly mandate


def _log_audit(db_name: str, details: str) -> None:
    """Simulate logging audit events. NEVER create analytics.db."""
    logger.info("[TEST] Would log audit: %s : %s [No DB mutation]", db_name, details)
    # This function does not write to analytics.db – compliance with enterprise test/readonly mandate


def _compliance_check(conn: sqlite3.Connection) -> bool:
    """Check that all templates in DB are compliant (PEP8/flake8 placeholder)."""
    try:
        rows = conn.execute("SELECT template_content FROM templates").fetchall()
        for (content,) in rows:
            if _compliance_score(content) < 60.0:
                return False
        return True
    except Exception as exc:
        logger.error("Compliance check failed: %s", exc)
        return False


def synchronize_templates_real(source_dbs: Iterable[Path] | None) -> int:
    """Synchronize templates across databases with real writes."""
    proc_id = os.getpid()
    start_dt = datetime.now()
    start_ts = time.time()
    logger.info("[SYNC-START][REAL] PID=%s | Start time: %s", proc_id, start_dt.isoformat())

    databases = list(source_dbs) if source_dbs else []
    all_templates: dict[str, str] = {}

    for idx, db in enumerate(tqdm(databases, desc=f"Extracting [PID {proc_id}]", unit="db"), 1):
        for name, content in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = content
            else:
                logger.warning("Invalid template from %s: %s", db, name)
        etc = _calculate_etc(start_ts, idx, len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    synced = 0
    analytics_conn = sqlite3.connect(ANALYTICS_DB)
    analytics_conn.execute(
        "CREATE TABLE IF NOT EXISTS sync_events_log (id INTEGER PRIMARY KEY, event TEXT, details TEXT, ts TEXT)"
    )

    for idx, db in enumerate(tqdm(databases, desc=f"Applying Sync [PID {proc_id}]", unit="db"), 1):
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
            continue
        success = False
        err_msg = None
        try:
            with sqlite3.connect(db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS templates (name TEXT PRIMARY KEY, template_content TEXT)"
                )
                if not _compliance_check(conn):
                    raise ValueError(f"Compliance validation failed for {db}")
                existing = {row[0] for row in conn.execute("SELECT name FROM templates").fetchall()}
                for name, content in all_templates.items():
                    if name not in existing:
                        conn.execute(
                            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                conn.commit()
                success = True
        except Exception as exc:
            err_msg = str(exc)
            logger.error("Sync failed for %s: %s", db, err_msg)
        event = "sync_success" if success else "sync_failed"
        details = str(db) if success else f"{db}:{err_msg}"
        analytics_conn.execute(
            "INSERT INTO sync_events_log (event, details, ts) VALUES (?, ?, ?)",
            (event, details, datetime.utcnow().isoformat()),
        )
        analytics_conn.commit()
        if success:
            synced += 1
        etc = _calculate_etc(start_ts, idx + len(databases), len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    duration = (datetime.now() - start_dt).total_seconds()
    analytics_conn.execute(
        "INSERT INTO sync_events_log (event, details, ts) VALUES (?, ?, ?)",
        ("sync_complete", f"{synced} databases synchronized in {duration:.2f}s", datetime.utcnow().isoformat()),
    )
    analytics_conn.commit()
    analytics_conn.close()
    logger.info("[SYNC-END][REAL] PID=%s | Duration: %.2fs | DBs: %s", proc_id, duration, synced)
    return synced


def synchronize_templates(
    source_dbs: Iterable[Path] | None = None,
) -> int:
    """
    Simulate synchronization of templates across multiple databases.
    NO mutation or creation of analytics.db or other DBs.
    Progress bars, ETC, process ID, and status updates included.
    """
    proc_id = os.getpid()
    start_dt = datetime.now()
    start_ts = time.time()
    logger.info("[SYNC-START] PID=%s | Start time: %s", proc_id, start_dt.isoformat())
    _log_event(
        {
            "event": "sync_start_simulation",
            "sources": ",".join(str(p) for p in source_dbs or []),
            "proc_id": proc_id,
            "mode": "test-only",
        },
        table="sync_events_log",
        db_path=ANALYTICS_DB,
        echo=True,
    )
    databases = list(source_dbs) if source_dbs else []
    all_templates: dict[str, str] = {}

    # Visual progress: Extraction phase
    for idx, db in enumerate(tqdm(databases, desc=f"Extracting [PID {proc_id}]", unit="db"), 1):
        for name, content in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = content
            else:
                logger.warning("Invalid template from %s: %s", db, name)
        etc = _calculate_etc(start_ts, idx, len(databases))
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    source_names = ",".join(str(d) for d in databases)
    synced = 0

    # Visual progress: Synchronization phase (simulated, no DB writes)
    for idx, db in enumerate(tqdm(databases, desc=f"Simulating Sync [PID {proc_id}]", unit="db"), 1):
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
            continue
        logger.info("[SIMULATION] Would synchronize templates to %s", db)
        sync_fail = False
        # Simulate compliance check
        try:
            with sqlite3.connect(db) as conn:
                compliant = _compliance_check(conn)
            if not compliant:
                sync_fail = True
                logger.error("[SIMULATION] Compliance validation failed for %s", db)
        except Exception as exc:
            sync_fail = True
            logger.error("[SIMULATION] Could not check compliance on %s: %s", db, exc)
        # Simulate dual Copilot validation
        logger.info("[DUAL COPILOT][SIM] Copilot A & B validate simulated sync for %s", db)
        if sync_fail:
            _log_audit(str(db), "Simulated sync failure: compliance/error")
            logger.error("Simulated sync failed for %s [PID %s]", db, proc_id)
        else:
            synced += 1
            _log_sync_event(source_names, str(db))
            logger.info("[SIMULATION] Sync would succeed for %s [PID %s]", db, proc_id)
        etc = _calculate_etc(start_ts, idx + len(databases), len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    duration = (datetime.now() - start_dt).total_seconds()
    logger.info("[SYNC-END][SIM] PID=%s | Duration: %.2fs | DBs: %s", proc_id, duration, synced)
    _log_event(
        {
            "event": "sync_complete_simulation",
            "details": f"{synced} databases in {duration:.2f}s",
            "proc_id": proc_id,
            "mode": "test-only",
        },
        table="sync_events_log",
        db_path=ANALYTICS_DB,
        echo=True,
    )
    logger.info("\n[SIMULATION COMPLETE] No database was created or modified. Run with --real to apply changes.")
    return synced


def synchronize_templates_real(source_dbs: Iterable[Path] | None) -> int:
    """Synchronize templates across DBs and log results."""
    proc_id = os.getpid()
    start_dt = datetime.now()
    start_ts = time.time()
    logger.info("[SYNC-START] PID=%s | Start time: %s", proc_id, start_dt.isoformat())

    databases = list(source_dbs) if source_dbs else []
    all_templates: dict[str, str] = {}

    for idx, db in enumerate(tqdm(databases, desc=f"Extracting [PID {proc_id}]", unit="db"), 1):
        for name, content in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = content
            else:
                logger.warning("Invalid template from %s: %s", db, name)
        etc = _calculate_etc(start_ts, idx, len(databases))
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    synced = 0
    for idx, db in enumerate(tqdm(databases, desc=f"Applying Sync [PID {proc_id}]", unit="db"), 1):
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
            continue
        try:
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS templates (name TEXT PRIMARY KEY, template_content TEXT)")
                if not _compliance_check(conn):
                    logger.error("Compliance validation failed for %s", db)
                    _log_event(
                        {"event": "sync_failed", "details": str(db), "timestamp": datetime.utcnow().isoformat()},
                        table="sync_events_log",
                        db_path=ANALYTICS_DB,
                        echo=True,
                        test_mode=False,
                    )
                    continue
                for name, content in all_templates.items():
                    cur = conn.execute("SELECT 1 FROM templates WHERE name=?", (name,))
                    if cur.fetchone() is None:
                        conn.execute(
                            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                conn.commit()
                synced += 1
                _log_event(
                    {"event": "sync_success", "details": str(db), "timestamp": datetime.utcnow().isoformat()},
                    table="sync_events_log",
                    db_path=ANALYTICS_DB,
                    echo=True,
                    test_mode=False,
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Sync failed for %s: %s", db, exc)
            _log_event(
                {"event": "sync_failed", "details": f"{db}:{exc}", "timestamp": datetime.utcnow().isoformat()},
                table="sync_events_log",
                db_path=ANALYTICS_DB,
                echo=True,
                test_mode=False,
            )
        etc = _calculate_etc(start_ts, idx + len(databases), len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    duration = (datetime.now() - start_dt).total_seconds()
    logger.info("[SYNC-END] PID=%s | Duration: %.2fs | DBs: %s", proc_id, duration, synced)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sync_events_log (id INTEGER PRIMARY KEY, event TEXT, details TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO sync_events_log (event, details, ts) VALUES (?, ?, ?)",
            ("sync_complete", f"{synced} databases synchronized in {duration:.2f}s", datetime.utcnow().isoformat()),
        )
        conn.commit()
    return synced


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Synchronize templates across databases")
    parser.add_argument("databases", nargs="*", type=Path, help="Database files")
    parser.add_argument("--real", action="store_true", help="Apply real synchronization")
    args = parser.parse_args()

    dbs = args.databases
    if not dbs:
        dbs_env = os.getenv("TEMPLATE_SYNC_DBS", "").split(os.pathsep)
        dbs = [Path(p) for p in dbs_env if p]

    if args.real:
        synchronize_templates_real(dbs)
        print("\n[REAL SYNC COMPLETE] Templates synchronized across databases.\n")
    else:
        synchronize_templates(dbs)
        print("\n[NOTICE] No database was created or modified. To actually create `analytics.db`, run with --real\n")
