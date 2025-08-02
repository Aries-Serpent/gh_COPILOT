"""
Objective similarity scoring utilities.

This module implements database-first, enterprise-grade similarity scoring for objectives
against code templates in production.db. All scoring events are logged in analytics.db.
Visual processing indicators, timeout controls, start time logging, ETC calculation,
and real-time status updates are enforced per enterprise standards and DUAL COPILOT pattern.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from tqdm import tqdm
from quantum.quantum_algorithm_library_expansion import quantum_text_score

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOGS_DIR = Path("logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"objective_similarity_scorer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    venv_root = workspace_root / ".venv"
    for folder in workspace_root.rglob("*"):
        if folder == workspace_root or not folder.is_dir() or str(folder).startswith(str(venv_root)):
            continue
        name_tokens = folder.name.lower().split("_")
        if any(tok in {"backup", "backups", "temp"} for tok in name_tokens):
            logging.error(f"Recursive folder detected: {folder}")
            raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


def _write_log(scores: List[Tuple[int, float]], objective: str) -> None:
    log_entry = {"timestamp": datetime.utcnow().isoformat(), "objective": objective, "scores": scores}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, indent=2) + "\n")


def compute_similarity_scores(
    objective: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
    timeout_minutes: int = 30,
    methods: List[str] | None = None,
    weights: List[float] | None = None,
    persist_json_dir: Path | None = None,
) -> List[Tuple[int, float]]:
    """
    Compute similarity scores between the objective and all templates in the production database.
    Uses TF-IDF vectorization and cosine similarity for scoring.
    Includes visual processing indicators, start time logging, timeout, ETC, and status updates.
    Logs all scores to analytics.db and /logs/template_rendering.
    """
    # Start time logging and anti-recursion validation
    start_time = datetime.now()
    process_id = os.getpid()
    timeout_seconds = timeout_minutes * 60
    logging.info("PROCESS STARTED: Objective Similarity Scoring")
    logging.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Process ID: {process_id}")
    validate_no_recursive_folders()

    # Fetch templates from production.db
    templates: List[Tuple[int, str]] = []
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            try:
                cur = conn.execute("SELECT id, template_code FROM code_templates")
                templates = [(row[0], row[1]) for row in cur.fetchall()]
            except sqlite3.Error as exc:
                logging.error(f"Error querying production.db: {exc}")
                templates = []
    if not templates:
        logging.warning("No templates found in production.db")
        return []

    if methods is None:
        methods = ["tfidf"]

    if weights is None:
        weights = [1.0 for _ in methods]
    elif isinstance(weights, dict):
        if not all(m in weights for m in methods):
            missing = [m for m in methods if m not in weights]
            raise ValueError(f"Missing weights for methods: {missing}")
        weights = [weights[m] for m in methods]

    if len(weights) != len(methods):
        raise ValueError("methods and weights must have the same length")
    # Prepare corpus and vectorizer
    corpus = [objective] + [t[1] for t in templates]
    vectorizer = TfidfVectorizer().fit(corpus)
    obj_vec = vectorizer.transform([objective])
    obj_q = quantum_text_score(objective) if "quantum" in methods else 0.0
    jaccard_vectorizer = CountVectorizer(binary=True).fit(corpus) if "jaccard" in methods else None
    obj_bin = jaccard_vectorizer.transform([objective]) if jaccard_vectorizer else None

    # Visual processing indicators: progress bar, ETC, timeout, status updates
    scores: List[Tuple[int, float]] = []
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    total_steps = len(templates)
    elapsed = 0.0
    with tqdm(total=total_steps, desc="Scoring Templates", unit="tmpl") as pbar:
        for idx, (tid, text) in enumerate(templates, 1):
            phase = f"Scoring template {tid}"
            pbar.set_description(phase)
            vec = vectorizer.transform([text])
            score = 0.0
            if "tfidf" in methods:
                score += weights[methods.index("tfidf")] * float(cosine_similarity(obj_vec, vec)[0][0])
            if "quantum" in methods:
                cand_q = quantum_text_score(text)
                qsim = 1.0 - abs(cand_q - obj_q)
                score += weights[methods.index("quantum")] * qsim
            if "jaccard" in methods and jaccard_vectorizer is not None and obj_bin is not None:
                cand_bin = jaccard_vectorizer.transform([text])
                obj_arr = obj_bin.toarray()[0]
                cand_arr = cand_bin.toarray()[0]
                intersect = (obj_arr & cand_arr).sum()
                union = (obj_arr | cand_arr).sum()
                jscore = float(intersect) / float(union) if union else 0.0
                score += weights[methods.index("jaccard")] * jscore
            scores.append((tid, score))
            with sqlite3.connect(analytics_db) as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS objective_similarity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        objective TEXT,
                        template_id INTEGER,
                        score REAL,
                        ts TEXT
                    )"""
                )
                conn.execute(
                    "INSERT INTO objective_similarity (objective, template_id, score, ts) VALUES (?, ?, ?, ?)",
                    (objective, tid, score, datetime.utcnow().isoformat()),
                )
                conn.commit()
            elapsed = time.time() - start_time.timestamp()
            etc = calculate_etc(start_time.timestamp(), idx, total_steps)
            pbar.set_postfix(ETC=etc)
            pbar.update(1)
            if elapsed > timeout_seconds:
                logging.error("Timeout exceeded during similarity scoring")
                raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
    logging.info(f"Objective similarity scoring completed in {elapsed:.2f}s | ETC: {etc}")
    _write_log(scores, objective)
    if persist_json_dir is not None:
        persist_json_dir.mkdir(parents=True, exist_ok=True)
        fname = f"similarity_scores_{hashlib.sha256(objective.encode()).hexdigest()[:8]}.json"
        with open(persist_json_dir / fname, "w", encoding="utf-8") as f:
            json.dump({"objective": objective, "scores": scores}, f, indent=2)
    return scores


def validate_scores(
    objective: str,
    expected_count: int,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> bool:
    """
    DUAL COPILOT validation for similarity scoring.
    Checks analytics.db for matching similarity events.
    """
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM objective_similarity WHERE objective = ?",
            (objective,),
        )
        count = cur.fetchone()[0]
    if count >= expected_count:
        logging.info("DUAL COPILOT validation passed: Objective similarity scoring integrity confirmed.")
        return True
    else:
        logging.error("DUAL COPILOT validation failed: Objective similarity scoring mismatch.")
        return False


__all__ = [
    "compute_similarity_scores",
    "validate_scores",
    "DEFAULT_PRODUCTION_DB",
    "DEFAULT_ANALYTICS_DB",
]
