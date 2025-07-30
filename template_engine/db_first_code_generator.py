"""Database-first template auto-generation utilities.

This module clusters templates using :class:`sklearn.cluster.KMeans` and
provides APIs to generate boilerplate code from existing patterns. Errors are
raised if invalid templates are encountered or if recursion safeguards fail.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Iterable

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from utils.log_utils import _log_event

from .placeholder_utils import DEFAULT_PRODUCTION_DB
from .objective_similarity_scorer import compute_similarity_scores
from .pattern_mining_engine import extract_patterns

# Quantum scoring helper
try:
    from quantum_algorithm_library_expansion import (
        quantum_text_score,
        quantum_similarity_score,
        quantum_cluster_score,
    )
except ImportError:  # pragma: no cover - optional dependency

    def quantum_text_score(text: str) -> float:
        """Gracefully degrade when quantum library is unavailable."""
        return 0.0

    def quantum_similarity_score(a: Iterable[float], b: Iterable[float]) -> float:
        """Gracefully degrade when quantum library is unavailable."""
        return 0.0

    def quantum_cluster_score(matrix: np.ndarray) -> float:
        return 0.0


DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")

LOGS_DIR = Path("logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"auto_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logger.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


class TemplateAutoGenerator:
    def __init__(
        self,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        completion_db: Path = DEFAULT_COMPLETION_DB,
        production_db: Path = DEFAULT_PRODUCTION_DB,
    ) -> None:
        self.analytics_db = analytics_db
        self.completion_db = completion_db
        self.production_db = production_db
        self.templates = self._load_templates()
        self.patterns = []
        self.cluster_vectorizer = None

    def _load_templates(self) -> List[str]:
        templates: List[str] = []
        if self.completion_db.exists():
            with sqlite3.connect(self.completion_db) as conn:
                try:
                    cur = conn.execute("SELECT template_content FROM templates")
                    templates = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading templates: {exc}")
        if not templates:
            from . import pattern_templates

            templates = list(pattern_templates.DEFAULT_TEMPLATES)
            logger.info(
                "Loaded %s default templates from pattern_templates",
                len(templates),
            )
        else:
            logger.info(f"Loaded {len(templates)} templates")
        _log_event(
            {"event": "load_templates", "count": len(templates)},
            table="generator_events",
            db_path=self.analytics_db,
        )
        return templates

    def _quantum_score(self, text: str) -> float:
        """Return a quantum-inspired score for ``text`` using helper module."""
        return quantum_text_score(text)

    def _quantum_similarity(self, a: str, b: str) -> float:
        """Return similarity between two texts using quantum scoring."""
        vec_a = [ord(c) for c in a]
        vec_b = [ord(c) for c in b]
        n = min(len(vec_a), len(vec_b))
        return quantum_similarity_score(vec_a[:n], vec_b[:n])

    def _load_production_patterns(self) -> list[str]:
        """Fetch template patterns from ``production.db`` if available."""
        patterns: list[str] = []
        if self.production_db.exists():
            with sqlite3.connect(self.production_db) as conn:
                try:
                    cur = conn.execute("SELECT template_content FROM script_template_patterns")
                    patterns = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading production patterns: {exc}")
        return patterns

    def _cluster_patterns(self) -> KMeans | None:
        logger.info("Clustering patterns and templates...")
        prod_patterns = self._load_production_patterns()
        corpus = self.templates + self.patterns + prod_patterns
        if not corpus:
            logger.warning("No corpus to cluster")
            return None
        self.cluster_vectorizer = TfidfVectorizer()
        matrix = self.cluster_vectorizer.fit_transform(corpus)
        n_clusters = min(len(corpus), 2)
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=int(time.time()))
        start_ts = time.time()
        with tqdm(total=1, desc="Clustering", unit="cluster") as pbar:
            model.fit(matrix)
            pbar.update(1)
        model.cluster_centers_ += np.random.normal(scale=0.01, size=model.cluster_centers_.shape)
        duration = time.time() - start_ts
        logger.info(f"Clustered {len(corpus)} items into {n_clusters} groups in {duration:.2f}s")
        _log_event(
            {
                "event": "cluster",
                "items": len(corpus),
                "clusters": n_clusters,
                "duration": duration,
            },
            table="generator_events",
            db_path=self.analytics_db,
        )
        return model

    def objective_similarity(self, a: str, b: str) -> float:
        vectorizer = TfidfVectorizer().fit([a, b])
        vecs = vectorizer.transform([a, b])
        return float(cosine_similarity(vecs[0], vecs[1])[0][0])

    def rank_templates(self, target: str) -> List[str]:
        """Return templates ranked by similarity to ``target``."""
        ranked: List[tuple[str, float]] = []
        q_target = self._quantum_score(target)
        if self.production_db.exists():
            scores = compute_similarity_scores(
                target,
                production_db=self.production_db,
                analytics_db=self.analytics_db,
                timeout_minutes=1,
            )
            id_to_score = {tid: score for tid, score in scores}
            with sqlite3.connect(self.production_db) as conn:
                try:
                    cur = conn.execute("SELECT id, template_code FROM code_templates")
                    rows = cur.fetchall()
                except sqlite3.Error as exc:  # pragma: no cover - missing table
                    logger.error(f"Error loading templates: {exc}")
                    rows = []
                for tid, text in rows:
                    if tid not in id_to_score:
                        continue
                    bonus = 0.0
                    pats = extract_patterns([text])
                    if any(p in target for p in pats):
                        bonus = 0.1
                    q_sim = self._quantum_similarity(target, text)
                    tfidf = self.objective_similarity(target, text)
                    q_text = 1.0 - abs(self._quantum_score(text) - q_target)
                    score = id_to_score[tid] + tfidf + q_sim + q_text + bonus
                    ranked.append((text, score))
                    _log_event({"event": "rank_eval", "target": target, "template_id": tid, "score": score}, table="generator_events", db_path=self.analytics_db)
                    _log_event({"event": "tfidf_score", "template_id": tid, "score": tfidf}, table="generator_events", db_path=self.analytics_db)
                    _log_event({"event": "quantum_text", "template_id": tid, "score": q_text}, table="generator_events", db_path=self.analytics_db)
        if not ranked:
            candidates = self.templates or self.patterns
            for tmpl in candidates:
                tfidf = self.objective_similarity(target, tmpl)
                q_sim = self._quantum_similarity(target, tmpl)
                q_text = 1.0 - abs(self._quantum_score(tmpl) - q_target)
                score = tfidf + q_sim + q_text
                ranked.append((tmpl, score))
                _log_event({"event": "rank_eval", "target": target, "template_id": -1, "score": score}, table="generator_events", db_path=self.analytics_db)
                _log_event({"event": "tfidf_score", "template_id": -1, "score": tfidf}, table="generator_events", db_path=self.analytics_db)
                _log_event({"event": "quantum_text", "template_id": -1, "score": q_text}, table="generator_events", db_path=self.analytics_db)
        ranked.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in ranked]

    def select_best_template(self, target: str, timeout: float = 30.0) -> str:
        logger.info(f"Selecting best template for target: {target}")
        ranked = self.rank_templates(target)
        if not ranked:
            logger.warning("No candidates available for selection")
            return ""
        best = ranked[0]
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "INSERT INTO generator_events (event, target, best_template, timestamp) VALUES (?, ?, ?, ?)",
                    ("select_best_template", target, best, datetime.now().isoformat()),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"Logging error in select_best_template: {exc}")
        return best


class DBFirstCodeGenerator(TemplateAutoGenerator):
    """Backward compatible wrapper for TemplateAutoGenerator."""

    def __init__(
        self,
        production_db: Path,
        documentation_db: Path,
        template_db: Path,
        analytics_db: Path,
    ) -> None:
        super().__init__(analytics_db=analytics_db, completion_db=template_db, production_db=production_db)
        self.documentation_db = documentation_db
        self.templates = []
        self.patterns = []

    def fetch_existing_pattern(self, name: str) -> str | None:  # pragma: no cover - simplified
        if self.production_db.exists():
            with sqlite3.connect(self.production_db) as conn:
                cur = conn.execute(
                    "SELECT template_content FROM script_template_patterns WHERE pattern_name=?",
                    (name,),
                )
                row = cur.fetchone()
                if row:
                    return row[0]
        return None

    def generate(self, objective: str) -> str:
        pattern = self.fetch_existing_pattern(objective)
        if pattern:
            result = pattern
        else:
            ranked = self.rank_templates(objective)
            result = ranked[0] if ranked else "Auto-generated template"
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS code_generation_events (objective TEXT, status TEXT)"
            )
            conn.execute(
                "INSERT INTO code_generation_events (objective, status) VALUES (?, 'generated')",
                (objective,),
            )
            conn.commit()
        return result

    def generate_integration_ready_code(self, objective: str) -> Path:
        path = Path(f"{objective}.py")
        path.write_text(self.generate(objective))
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS code_generation_events (objective TEXT, status TEXT)"
            )
            conn.execute(
                "INSERT INTO code_generation_events (objective, status) VALUES (?, 'integration-ready')",
                (objective,),
            )
            conn.commit()
        return path
