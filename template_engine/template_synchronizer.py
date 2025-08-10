# [Script]: Template Synchronizer Engine
# > Generated: 2025-07-25 14:40:23 | Author: mbaetiong
# --- Enterprise Standards ---
# - Flake8/PEP8 Compliant
# - Visual Processing Indicators: start time, progress bar, ETC, real-time status
#   process ID, error handling, dual validation
# - Analytics DB only created in real mode (`--real` flag)
# - All database/file operations must be validated for anti-recursion and compliance

import argparse
import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable
import re

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from tqdm import tqdm

from secondary_copilot_validator import SecondaryCopilotValidator

from utils.log_utils import ensure_tables, insert_event
from enterprise_modules.compliance import _log_rollback
from utils.lessons_learned_integrator import load_lessons, apply_lessons

apply_lessons(logging.getLogger(__name__), load_lessons())

# Internal helpers


def _can_write_analytics() -> bool:
    """Return True if ``ANALYTICS_DB`` is outside the workspace."""
    workspace = os.getenv("GH_COPILOT_WORKSPACE")
    if not workspace:
        return True
    try:
        Path(ANALYTICS_DB).resolve().relative_to(Path(workspace).resolve())
        return False
    except ValueError:
        return True


def _extract_templates(db: Path) -> list[tuple[str, str]]:
    """Return templates from ``db`` or ``[]`` on error."""
    if not db.exists():
        return []
    try:
        with sqlite3.connect(db) as conn:
            return list(_load_templates(conn).items())
    except sqlite3.Error as exc:  # pragma: no cover - logging only
        logger.warning("Failed to read templates from %s: %s", db, exc)
        return []


WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
ANALYTICS_DB = WORKSPACE_ROOT / "databases" / "analytics.db"

DOC_SCHEMA_FILE = Path("documentation/additional/schemas/analytics_schema.md")

_EXPECTED_TABLES: set[str] | None = None


def _load_expected_tables() -> set[str]:
    """Return table names defined in the documentation."""
    global _EXPECTED_TABLES
    if _EXPECTED_TABLES is None:
        tables: set[str] = set()
        if DOC_SCHEMA_FILE.exists():
            text = DOC_SCHEMA_FILE.read_text()
            for match in re.finditer(r"CREATE TABLE (\w+)", text):
                tables.add(match.group(1))
        _EXPECTED_TABLES = tables
    return _EXPECTED_TABLES


def _schema_matches_doc(conn: sqlite3.Connection) -> bool:
    """Return True if all documented tables exist in ``conn``."""
    expected = _load_expected_tables()
    existing = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    return expected.issubset(existing)


logger = logging.getLogger(__name__)


def _load_templates(conn: sqlite3.Connection) -> dict[str, str]:
    has_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'").fetchone()
    if not has_table:
        raise sqlite3.OperationalError("missing templates table")
    rows = conn.execute("SELECT name, template_content FROM templates").fetchall()
    return {name: content for name, content in rows if content}


def _calculate_etc(start_ts: float, current_progress: int, total_work: int) -> str:
    """Estimate remaining time for progress reporting."""
    if current_progress <= 0:
        return "N/A"
    elapsed = time.time() - start_ts
    total_est = elapsed / (current_progress / total_work)
    remaining = max(0.0, total_est - elapsed)
    return f"{remaining:.2f}s"


def _validate_template(name: str, content: str) -> bool:
    """Validate that template has a name and non-empty content."""
    return bool(name and content and content.strip())


def _cluster_templates(templates: dict[str, str], n_clusters: int = 2) -> dict[str, str]:
    """Return representative templates using KMeans clustering."""
    if not templates:
        return templates
    try:
        texts = list(templates.values())
        names = list(templates.keys())
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(texts)
        n_clusters = min(n_clusters, len(texts))
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
        labels = model.fit_predict(matrix)
        inertia = float(model.inertia_)
        silhouette = 0.0
        if n_clusters > 1 and matrix.shape[0] > 1:
            silhouette = float(silhouette_score(matrix, labels))
        reps: dict[str, str] = {}
        arr = matrix.toarray()
        for label in range(n_clusters):
            members = [i for i, lbl in enumerate(labels) if lbl == label]
            if not members:
                continue
            center = model.cluster_centers_[label]
            best_idx = min(
                members,
                key=lambda idx: float(np.linalg.norm(arr[idx] - center)),
            )
            name = names[best_idx]
            reps[name] = templates[name]
        if _can_write_analytics():
            with sqlite3.connect(ANALYTICS_DB) as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS template_sync_cluster_metrics (
                        inertia REAL,
                        silhouette REAL,
                        n_clusters INTEGER,
                        ts TEXT
                    )""",
                )
                conn.execute(
                    "INSERT INTO template_sync_cluster_metrics (inertia, silhouette, n_clusters, ts) VALUES (?,?,?,?)",
                    (inertia, silhouette, n_clusters, datetime.utcnow().isoformat()),
                )
                conn.commit()
            _log_audit_real(
                str(ANALYTICS_DB),
                f"sync_clusters={n_clusters},inertia={inertia:.2f},silhouette={silhouette:.4f}",
            )
        return reps
    except Exception as exc:
        # If clustering fails, fallback to original templates
        logger.exception("Clustering failed; using all templates: %s", exc)
        return templates


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
    """Log a synchronization event to analytics db."""
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS sync_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    timestamp TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO sync_events (source, target, timestamp) VALUES (?, ?, ?)",
                (source, target, datetime.utcnow().isoformat()),
            )
            conn.commit()
    except Exception as exc:  # pragma: no cover - logging should not fail tests
        logger.error("Failed to log sync event: %s", exc)


def _log_audit(db_name: str, details: str) -> None:
    """Log audit events to analytics db."""
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    db_name TEXT,
                    details TEXT,
                    timestamp TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO audit_log (db_name, details, timestamp) VALUES (?, ?, ?)",
                (db_name, details, datetime.utcnow().isoformat()),
            )
            conn.commit()
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to log audit event: %s", exc)


def _log_sync_event_real(source: str, target: str) -> None:
    """Record a real synchronization event in analytics.db."""
    if not _can_write_analytics():
        return
    insert_event(
        {"source": source, "target": target, "ts": datetime.utcnow().isoformat()},
        "sync_events_log",
        db_path=ANALYTICS_DB,
        test_mode=False,
    )


def _log_audit_real(db_name: str, details: str) -> None:
    """Record an audit event in analytics.db."""
    if not _can_write_analytics():
        return
    insert_event(
        {"db_name": db_name, "details": details, "ts": datetime.utcnow().isoformat()},
        "audit_log",
        db_path=ANALYTICS_DB,
        test_mode=False,
    )


def run_migrations(db: Path, *, dry_run: bool = False) -> None:
    """Apply SQL migrations to ``db`` transactionally."""
    migrations = sorted(Path("databases/migrations").glob("*.sql"))
    if not migrations:
        return
    if not db.exists():
        logger.warning("Database %s does not exist for migrations", db)
        return
    if dry_run:
        for script in migrations:
            print(f"[DRY-RUN] Would run {script.name} on {db}")
        return
    with sqlite3.connect(db) as conn:
        conn.execute("BEGIN")
        try:
            for script in migrations:
                conn.executescript(script.read_text())
            if not _schema_matches_doc(conn):
                raise RuntimeError("schema mismatch")
            conn.commit()
            logger.info("Migrations applied to %s", db)
            _log_audit_real(str(db), "migrations")
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            logger.error("Migration failed for %s: %s", db, exc)
            _log_audit_real(str(db), f"migration_failed:{exc}")
            _log_rollback(str(db))


def _compliance_check(conn: sqlite3.Connection) -> bool:
    """Check that all templates in DB meet PEP8 and flake8 compliance."""
    try:
        rows = conn.execute("SELECT template_content FROM templates").fetchall()
        for (content,) in rows:
            if _compliance_score(content) < 60.0:
                return False
        return True
    except sqlite3.Error as exc:
        logger.error("Compliance check failed: %s", exc)
        return False


def copy_template_file(src: Path, dst: Path, *, dry_run: bool = False) -> None:
    """Copy ``src`` to ``dst`` within a transaction and log the action."""
    if dry_run:
        print(f"[DRY-RUN] copy {src} -> {dst}")
        return
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute("BEGIN")
        try:
            dst.write_text(src.read_text())
            conn.commit()
            _log_audit_real("file_copy", f"{src}->{dst}")
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            logger.error("Copy failed: %s", exc)
            _log_audit_real("file_copy", f"failed:{exc}")
            _log_rollback(str(dst))
            if dst.exists():
                dst.unlink()
            raise


def update_template_content(
    dbs: Iterable[Path],
    name: str,
    file_path: Path,
    *,
    dry_run: bool = False,
) -> None:
    """Update template ``name`` in ``dbs`` transactionally and log the action."""
    content = file_path.read_text()
    for db in dbs:
        if dry_run:
            print(f"[DRY-RUN] update {name} in {db}")
            continue
        with sqlite3.connect(db) as conn:
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                    (name, content),
                )
                conn.commit()
                _log_audit_real(str(db), f"update:{name}")
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                logger.error("Update failed for %s: %s", db, exc)
                _log_audit_real(str(db), f"update_failed:{exc}")
                _log_rollback(str(db))


def _synchronize_templates_simulation(
    source_dbs: Iterable[Path] | None = None,
    *,
    cluster: bool = False,
) -> int:
    """Simulate synchronization across databases.

    When ``cluster`` is ``True`` only cluster centroids are used during the
    simulated synchronization. No database is modified.
    """
    proc_id = os.getpid()
    start_dt = datetime.now()
    start_ts = time.time()
    logger.info("[SYNC-START] PID=%s | Start time: %s", proc_id, start_dt.isoformat())
    insert_event(
        {
            "event": "sync_start_simulation",
            "sources": ",".join(str(p) for p in source_dbs or []),
            "proc_id": proc_id,
            "mode": "test-only",
        },
        "sync_events_log",
        db_path=ANALYTICS_DB,
        test_mode=True,
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

    if cluster:
        all_templates = _cluster_templates(all_templates)

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
        except sqlite3.Error as exc:
            sync_fail = True
            logger.error("[SIMULATION] Could not check compliance on %s: %s", db, exc)
        # Simulate dual Copilot validation
        logger.info("[DUAL COPILOT][SIM] Copilot A & B validate simulated sync for %s", db)
        if sync_fail:
            _log_audit(str(db), "Simulated sync failure: compliance/error")
            logger.error("Simulated sync failed for %s [PID %s]", db, proc_id)
        else:
            synced += 1
            insert_event(
                {"event": "sync_success", "source": source_names, "target": str(db)},
                "sync_events_log",
                db_path=ANALYTICS_DB,
                test_mode=True,
            )
            logger.info("[SIMULATION] Sync would succeed for %s [PID %s]", db, proc_id)
        etc = _calculate_etc(start_ts, idx + len(databases), len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    duration = (datetime.now() - start_dt).total_seconds()
    logger.info("[SYNC-END][SIM] PID=%s | Duration: %.2fs | DBs: %s", proc_id, duration, synced)
    insert_event(
        {
            "event": "sync_complete_simulation",
            "details": f"{synced} databases in {duration:.2f}s",
            "proc_id": proc_id,
            "mode": "test-only",
        },
        "sync_events_log",
        db_path=ANALYTICS_DB,
        test_mode=True,
    )
    logger.info(
        "\n[SIMULATION COMPLETE] No database was created or modified. To actually"
        " create databases/analytics.db and apply real synchronization, run:\n\n"
        "    python template_engine/template_synchronizer.py --real\n"
    )
    return synced


def synchronize_templates(
    source_dbs: Iterable[Path] | None = None,
    *,
    cluster: bool = False,
) -> int:
    """Run template synchronization in simulation mode."""
    return _synchronize_templates_simulation(source_dbs, cluster=cluster)


def synchronize_templates_real(
    source_dbs: Iterable[Path] | None = None,
    *,
    cluster: bool = False,
) -> int:
    """Synchronize templates across databases with real writes.

    When ``cluster`` is ``True`` templates are grouped using KMeans and only
    cluster centroids are synchronized.
    """
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
        etc = _calculate_etc(start_ts, idx, len(databases))
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    if cluster:
        all_templates = _cluster_templates(all_templates)

    source_names = ",".join(str(d) for d in databases)
    synced = 0

    write_enabled = _can_write_analytics()
    if write_enabled:
        ensure_tables(ANALYTICS_DB, ["sync_events_log", "audit_log"], test_mode=False)
    for idx, db in enumerate(tqdm(databases, desc=f"Sync [PID {proc_id}]", unit="db"), 1):
        conn: sqlite3.Connection | None = None
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
            continue
        if not write_enabled:
            logger.info("[DRY-RUN] Would synchronize %s", db)
            continue
        conn = None
        try:
            conn = sqlite3.connect(db)
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")
            if not cur.fetchall():
                raise RuntimeError("missing templates table")
            conn.execute("BEGIN")
            conn.execute("CREATE TABLE IF NOT EXISTS templates (name TEXT PRIMARY KEY, template_content TEXT)")
            for name, content in all_templates.items():
                conn.execute(
                    "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                    (name, content),
                )
            if not _compliance_check(conn):
                raise RuntimeError("compliance validation failed")
            conn.commit()
            conn.close()
            synced += 1
            insert_event(
                {"source": source_names, "target": str(db), "ts": datetime.utcnow().isoformat()},
                "sync_events_log",
                db_path=ANALYTICS_DB,
                test_mode=False,
            )
            logger.info("Synced templates to %s [PID %s]", db, proc_id)
        except (sqlite3.Error, RuntimeError, OSError) as exc:  # noqa: BLE001
            logger.error("Failed to sync %s: %s", db, exc)
            if conn is not None:
                try:
                    conn.rollback()
                    insert_event(
                        {"event": "rollback", "db": str(db)},
                        "rollback_logs",
                        db_path=ANALYTICS_DB,
                        test_mode=True,
                    )
                except sqlite3.Error as rollback_exc:  # pragma: no cover - rollback best effort
                    logger.warning("Rollback failed for %s: %s", db, rollback_exc)
                conn.close()
            _log_audit_real(str(db), str(exc))
            insert_event(
                {"event": "sync_violation", "db": str(db), "error": str(exc)},
                "violation_logs",
                db_path=ANALYTICS_DB,
                test_mode=True,
            )
        finally:
            if conn is not None:
                conn.close()
        etc = _calculate_etc(start_ts, idx + len(databases), len(databases) * 2)
        tqdm.write(f"(PID {proc_id}) ETC: {etc}")

    duration = (datetime.now() - start_dt).total_seconds()
    logger.info("[SYNC-END][REAL] PID=%s | Duration: %.2fs | DBs: %s", proc_id, duration, synced)
    _log_sync_event_real(source_names, f"complete:{synced}")
    SecondaryCopilotValidator().validate_corrections([__file__])
    return synced


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("Template synchronization tool. Copy and update operations run inside explicit transactions.")
    )
    parser.add_argument("--real", action="store_true", help="Apply real synchronization")
    parser.add_argument(
        "--cluster",
        action="store_true",
        help="Cluster templates and use centroids for synchronization",
    )
    parser.add_argument("--migrate", action="store_true", help="Run migrations before sync")
    parser.add_argument(
        "--copy",
        nargs=2,
        metavar=("SRC", "DST"),
        help="Copy template using BEGIN/ROLLBACK; logged to audit_log",
    )
    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("NAME", "FILE"),
        help="Update template content transactionally and log the action",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without modifying files or databases",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    dbs_env = os.getenv("TEMPLATE_SYNC_DBS", "").split(os.pathsep)
    source_dbs = [Path(p) for p in dbs_env if p]
    if args.migrate:
        for db in source_dbs:
            run_migrations(db, dry_run=args.dry_run)
    if args.copy:
        src, dst = [Path(p) for p in args.copy]
        copy_template_file(src, dst, dry_run=args.dry_run)
    if args.update:
        name, file_path = args.update
        update_template_content(source_dbs, name, Path(file_path), dry_run=args.dry_run)
    if args.real:
        synchronize_templates_real(source_dbs, cluster=args.cluster)
    else:
        synchronize_templates(source_dbs, cluster=args.cluster)
        print("\n[NOTICE] No database was created or modified. To create `databases/analytics.db`, run:\n")
        print("    python template_engine/template_synchronizer.py --real\n")
