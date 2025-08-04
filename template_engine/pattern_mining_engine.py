"""Pattern mining utilities for extracting and logging templates.

This module provides helper functions used by :mod:`template_engine` for
mining patterns from stored templates. Functions log operations to
``analytics.db`` and implement safety checks, including anti-recursion
validation via :func:`validate_no_recursive_folders`.

All public functions raise ``RuntimeError`` on validation failure and
``sqlite3.Error`` for database issues so callers can react accordingly.
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

from .template_synchronizer import _log_audit_real
from utils.log_utils import _log_event
from utils.lessons_learned_integrator import load_lessons, apply_lessons

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOGS_DIR = Path("artifacts/logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"pattern_mining_engine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)

apply_lessons(logging.getLogger(__name__), load_lessons())


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd())))
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                # Avoid false positives for directories like "template_engine" or "templates"
                if folder.name.startswith("template"):
                    continue
                logging.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def ingest_assets(
    doc_dir: Path,
    tmpl_dir: Path,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> None:
    """Ingest documentation and template assets into ``production_db``."""
    production_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(production_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS asset_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                asset_type TEXT,
                digest TEXT,
                ts TEXT
            )"""
        )
        for base, a_type in [(doc_dir, "doc"), (tmpl_dir, "template")]:
            if not base or not base.exists():
                continue
            for path in base.rglob("*"):
                if path.is_file():
                    h = hashlib.sha256(path.read_bytes()).hexdigest()
                    conn.execute(
                        "INSERT INTO asset_inventory (path, asset_type, digest, ts) VALUES (?,?,?,?)",
                        (str(path), a_type, h, datetime.utcnow().isoformat()),
                    )
                    _log_event(
                        {"event": "asset_ingested", "path": str(path), "type": a_type},
                        table="ingestion_events",
                        db_path=analytics_db,
                    )
        conn.commit()


def extract_patterns(templates: List[str]) -> List[str]:
    """
    Extract recurring 3-word patterns from templates.
    """
    patterns = set()
    for text in templates:
        words = re.findall(r"\w+", text)
        for i in range(len(words) - 2):
            patterns.add(" ".join(words[i : i + 3]))
    return list(patterns)


def cluster_templates(features: List[List[float]], n_clusters: int = 5) -> List[int]:
    """Cluster templates based on numeric features using KMeans.

    Parameters
    ----------
    features: List[List[float]]
        Feature vectors representing templates.
    n_clusters: int, optional
        Desired number of clusters, default is 5.

    Returns
    -------
    List[int]
        Cluster label for each feature vector. Returns an empty list when
        ``features`` is empty.
    """
    if not features:
        return []
    data = np.array(features)
    k = min(len(data), n_clusters)
    model = KMeans(n_clusters=k, n_init="auto", random_state=0)
    return model.fit_predict(data).tolist()


def _log_patterns(patterns: List[str], analytics_db: Path) -> None:
    """Log mined patterns and associated compliance records."""
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    for pat in tqdm(patterns, desc="Logging Patterns", unit="pat"):
        _log_pattern(analytics_db, pat)


def _log_pattern(analytics_db: Path, pattern: str) -> None:
    """Log a single pattern to ``analytics_db`` with audit and compliance info."""
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS pattern_mining_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                ts TEXT
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS compliance_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compliance_type TEXT,
                status TEXT,
                last_check TEXT,
                next_check TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO pattern_mining_log (pattern, ts) VALUES (?, ?)",
            (pattern, timestamp),
        )
        conn.execute(
            "INSERT INTO compliance_tracking (compliance_type, status, last_check, next_check) VALUES (?, ?, ?, ?)",
            (pattern, "logged", timestamp, timestamp),
        )
        conn.commit()
    _log_audit_real(str(analytics_db), f"pattern_logged:{pattern}")


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


def mine_patterns(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
    timeout_minutes: int = 30,
) -> List[str]:
    """
    Mine templates in production_db and store discovered patterns.
    Includes visual processing indicators, start time logging, timeout, ETC, and status updates.
    Logs all patterns to analytics.db and /logs/template_rendering.
    """
    validate_no_recursive_folders()
    start_dt = datetime.now()
    start_ts = time.time()
    timeout_seconds = timeout_minutes * 60
    process_id = os.getpid()
    logging.info("PROCESS STARTED: Pattern Mining Engine")
    logging.info(f"Start Time: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Process ID: {process_id}")
    templates = []
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            try:
                cur = conn.execute("SELECT template_code FROM code_templates")
                templates = [row[0] for row in cur.fetchall()]
            except sqlite3.Error as exc:
                logging.error(f"Error querying production.db: {exc}")
                templates = []
    if not templates:
        logging.warning("No templates found in production.db")
        return []
    patterns = extract_patterns(templates)
    total_steps = len(patterns)
    etc = "N/A"
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS mined_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT,
                    mined_at TEXT
                )"""
            )
            for idx, pat in enumerate(tqdm(patterns, desc="Storing Patterns", unit="pat"), 1):
                conn.execute(
                    "INSERT INTO mined_patterns (pattern, mined_at) VALUES (?, ?)",
                    (pat, datetime.utcnow().isoformat()),
                )
                _log_audit_real(str(analytics_db), f"pattern_mined:{pat}")
                etc = calculate_etc(start_ts, idx, total_steps)
                if time.time() - start_ts > timeout_seconds:
                    raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
                if idx % 10 == 0 or idx == total_steps:
                    logging.info(f"Pattern {idx}/{total_steps} stored | ETC: {etc}")
            conn.commit()
        _log_patterns(patterns, analytics_db)
    cluster_count = 0
    if patterns:
        vec = TfidfVectorizer().fit_transform(patterns)
        model = KMeans(n_clusters=min(len(patterns), 2), n_init="auto", random_state=0)
        labels = model.fit_predict(vec)
        cluster_count = len(set(labels))
        inertia = float(model.inertia_)
        silhouette = 0.0
        if len(set(labels)) > 1 and vec.shape[0] > 1:
            silhouette = float(silhouette_score(vec, labels))
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS pattern_clusters (
                    pattern TEXT,
                    cluster INTEGER,
                    ts TEXT
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS pattern_cluster_metrics (
                    inertia REAL,
                    silhouette REAL,
                    n_clusters INTEGER,
                    ts TEXT
                )"""
            )
            for pat, label in zip(patterns, labels):
                if time.time() - start_ts > timeout_seconds:
                    raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
                conn.execute(
                    "INSERT INTO pattern_clusters (pattern, cluster, ts) VALUES (?,?,?)",
                    (pat, int(label), datetime.utcnow().isoformat()),
                )
            conn.execute(
                "INSERT INTO pattern_cluster_metrics (inertia, silhouette, n_clusters, ts) VALUES (?,?,?,?)",
                (inertia, silhouette, cluster_count, datetime.utcnow().isoformat()),
            )
            conn.commit()
    _log_audit_real(str(analytics_db), f"clusters={cluster_count},inertia={inertia:.2f},silhouette={silhouette:.4f}")
    logging.info(
        "Pattern mining completed in %.2fs | ETC: %s",
        time.time() - start_ts,
        calculate_etc(start_ts, total_steps, total_steps),
    )
    return patterns


def get_clusters(analytics_db: Path = DEFAULT_ANALYTICS_DB) -> Dict[int, List[str]]:
    """Return clustered patterns from ``analytics_db``.

    The mapping is ``cluster_id -> [patterns]``. Returns an empty
    dictionary when no clusters have been logged.
    """
    if not analytics_db.exists():
        return {}
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS pattern_clusters (
                pattern TEXT,
                cluster INTEGER,
                ts TEXT
            )"""
        )
        rows = conn.execute("SELECT pattern, cluster FROM pattern_clusters").fetchall()
    clusters: Dict[int, List[str]] = {}
    for pattern, cluster_id in rows:
        clusters.setdefault(int(cluster_id), []).append(pattern)
    return clusters


def get_cluster_metrics(analytics_db: Path = DEFAULT_ANALYTICS_DB) -> dict | None:
    """Return the most recent cluster metrics from ``analytics_db``."""
    if not analytics_db.exists():
        return None
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS pattern_cluster_metrics (
                inertia REAL,
                silhouette REAL,
                n_clusters INTEGER,
                ts TEXT
            )"""
        )
        row = conn.execute(
            "SELECT inertia, silhouette, n_clusters FROM pattern_cluster_metrics ORDER BY ts DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    inertia, silhouette, n_clusters = row
    return {
        "inertia": float(inertia),
        "silhouette": float(silhouette),
        "n_clusters": int(n_clusters),
    }


def aggregate_cross_references(analytics_db: Path = DEFAULT_ANALYTICS_DB) -> Dict[str, int]:
    """Aggregate cross-link events from ``analytics_db`` by file path."""
    if not analytics_db.exists():
        return {}
    counts: Dict[str, int] = {}
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS cross_reference_aggregate (
                file_path TEXT,
                links INTEGER,
                ts TEXT
            )"""
        )
        rows = conn.execute("SELECT file_path, COUNT(*) FROM cross_link_events GROUP BY file_path").fetchall()
        for path, num in rows:
            counts[path] = int(num)
            conn.execute(
                "INSERT INTO cross_reference_aggregate (file_path, links, ts) VALUES (?,?,?)",
                (path, int(num), datetime.utcnow().isoformat()),
            )
        conn.commit()
    _log_audit_real(str(analytics_db), f"cross_refs={len(counts)}")
    return counts


def validate_mining(expected_count: int, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    """
    DUAL COPILOT validation for pattern logging.
    Checks analytics.db for matching mining events.
    """
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM pattern_mining_log")
        count = cur.fetchone()[0]
    if count >= expected_count:
        logging.info("DUAL COPILOT validation passed: Pattern mining integrity confirmed.")
        return True
    else:
        logging.error("DUAL COPILOT validation failed: Pattern mining mismatch.")
        return False


__all__ = [
    "extract_patterns",
    "cluster_templates",
    "mine_patterns",
    "get_clusters",
    "get_cluster_metrics",
    "aggregate_cross_references",
    "validate_mining",
]
