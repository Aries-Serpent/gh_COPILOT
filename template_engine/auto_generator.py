"""Database-first template auto-generation utilities.

This module clusters templates using :class:`sklearn.cluster.KMeans` and
provides APIs to generate boilerplate code from existing patterns. Errors are
raised if invalid templates are encountered or if recursion safeguards fail.

If the optional quantum scoring library cannot be imported, the quantum scoring
functions fall back to returning ``0.0``.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Iterable

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from utils.log_utils import _log_event
from utils.lessons_learned_integrator import load_lessons, apply_lessons

from .pattern_templates import get_pattern_templates
from .learning_templates import get_lesson_templates
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
    from importlib import import_module

    try:
        _qal = import_module("quantum_algorithm_library_expansion")
    except ImportError as exc:
        logging.getLogger(__name__).debug(
            "Quantum library import failed: %s", exc
        )
        _qal = None

    if _qal is not None:

        def quantum_text_score(text: str) -> float:
            """Fallback invoking :mod:`quantum_algorithm_library_expansion`."""
            return _qal.quantum_text_score(text)

        def quantum_similarity_score(a: Iterable[float], b: Iterable[float]) -> float:
            """Fallback invoking :mod:`quantum_algorithm_library_expansion`."""
            return _qal.quantum_similarity_score(a, b)

        def quantum_cluster_score(matrix: np.ndarray) -> float:
            """Fallback invoking :mod:`quantum_algorithm_library_expansion`."""
            return _qal.quantum_cluster_score(matrix)
    else:

        def quantum_text_score(text: str) -> float:
            """Return a default score when quantum library is unavailable."""
            return 0.0

        def quantum_similarity_score(a: Iterable[float], b: Iterable[float]) -> float:
            """Return a default score when quantum library is unavailable."""
            return 0.0

        def quantum_cluster_score(matrix: np.ndarray) -> float:
            """Return a default score when quantum library is unavailable."""
            return 0.0


DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")

LOGS_DIR = Path("artifacts/logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"auto_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd())))
    # Flag directories that are obvious recursion risks
    forbidden_substrings = ["backup"]
    forbidden_exact = {"temp"}
    excluded_names = {".venv", "tmp"}
    for folder in workspace_root.rglob("*"):
        if not folder.is_dir() or folder == workspace_root:
            continue
        if any(name in folder.parts for name in excluded_names):
            continue
        name_lower = folder.name.lower()
        if name_lower in forbidden_exact or any(sub in name_lower for sub in forbidden_substrings):
            logger.error(f"Recursive folder detected: {folder}")
            raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


@dataclass
class TemplateAutoGenerator:
    """Generate and cluster templates loaded from SQLite databases with visual processing indicators.

    Templates are cached per target string to avoid redundant database lookups.
    """

    analytics_db: Path = DEFAULT_ANALYTICS_DB
    completion_db: Path = DEFAULT_COMPLETION_DB
    production_db: Path = DEFAULT_PRODUCTION_DB
    template_cache: dict[str, list[str]] = None

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        if self.template_cache is None:
            self.template_cache = {}
        _log_event(
            {"event": "init_start", "timestamp": datetime.utcnow().isoformat()},
            table="generator_events",
            db_path=self.analytics_db,
        )
        start_time = datetime.now()
        logger.info("PROCESS STARTED: TemplateAutoGenerator Initialization")
        logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
        validate_no_recursive_folders()
        # DB-first loading of patterns, lessons, and templates
        self.lessons = load_lessons()
        apply_lessons(logger, self.lessons)
        self.patterns = self._load_patterns()
        lesson_descriptions = [lesson["description"] for lesson in self.lessons]
        self.templates = (
            lesson_descriptions
            + self._load_templates()
            + get_pattern_templates()
            + list(get_lesson_templates().values())
        )
        self.cluster_vectorizer = None
        self.cluster_model = self._cluster_patterns()
        self._last_objective: dict[str, Any] | None = None
        duration = (datetime.now() - start_time).total_seconds()
        _log_event(
            {"event": "init_complete", "duration": duration},
            table="generator_events",
            db_path=self.analytics_db,
        )
        logger.info(f"Initialization completed in {duration:.2f}s")

    def _load_patterns(self) -> List[str]:
        logger.info("Loading patterns from analytics DB...")
        patterns = []
        if self.analytics_db.exists():
            with sqlite3.connect(self.analytics_db) as conn:
                try:
                    cur = conn.execute("SELECT replacement_template FROM ml_pattern_optimization")
                    patterns = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading patterns: {exc}")
        logger.info(f"Loaded {len(patterns)} patterns")
        _log_event(
            {"event": "load_patterns", "count": len(patterns)},
            table="generator_events",
            db_path=self.analytics_db,
        )
        return patterns

    def _load_production_templates(self) -> List[str]:
        """Fetch templates from ``production.db`` if available."""
        templates: List[str] = []
        if self.production_db.exists():
            with sqlite3.connect(self.production_db) as conn:
                try:
                    cur = conn.execute("SELECT template_code FROM code_templates")
                    templates = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading production templates: {exc}")
        return templates

    def _refresh_templates(self) -> None:
        """Reload templates and patterns from their databases."""
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_vectorizer = None
        self.cluster_model = self._cluster_patterns()
        if self.cluster_model is not None:
            self.cluster_model.cluster_centers_ += np.random.normal(
                scale=0.01, size=self.cluster_model.cluster_centers_.shape
            )

    def _load_templates(self) -> List[str]:
        logger.info("Loading templates from production DB then completion DB...")
        templates: List[str] = []
        templates.extend(self._load_production_templates())
        if not templates and self.completion_db.exists():
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
        return quantum_similarity_score(vec_a, vec_b)

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
        # Use a deterministic seed to ensure repeatable clustering results
        # across invocations. Previous versions seeded the algorithm with the
        # current timestamp which caused regenerated templates to differ on
        # subsequent runs, breaking reproducibility guarantees relied upon by
        # ``CompleteTemplateGenerator`` and its tests.
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
        start_ts = time.time()
        with tqdm(total=1, desc="clustering", unit="step") as pbar:
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
        if target in self.template_cache:
            _log_event(
                {"event": "cache_hit", "target": target},
                table="generator_events",
                db_path=self.analytics_db,
            )
            return self.template_cache[target]

        ranked: List[tuple[str, float]] = []
        vectorizer = TfidfVectorizer()
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
                cur = conn.execute("SELECT id, template_code FROM code_templates")
                for tid, text in cur.fetchall():
                    if tid not in id_to_score:
                        continue
                    bonus = 0.0
                    pats = extract_patterns([text])
                    if any(p in target for p in pats):
                        bonus = 0.1
                    vecs = vectorizer.fit_transform([target, text]).toarray()
                    tfidf = float(cosine_similarity([vecs[0]], [vecs[1]])[0][0])
                    q_sim = self._quantum_similarity(target, text)
                    q_vec = quantum_similarity_score(vecs[0], vecs[1])
                    q_text = 1.0 - abs(self._quantum_score(text) - q_target)
                    c_score = quantum_cluster_score(np.vstack([vecs[0], vecs[1]]))
                    q_total = float(np.mean([q_sim, q_vec, q_text, c_score]))
                    score = id_to_score[tid] + tfidf * q_total + bonus
                    ranked.append((text, score))
                    _log_event(
                        {"event": "rank_eval", "target": target, "template_id": tid, "score": score},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "tfidf_score", "template_id": tid, "score": tfidf},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "quantum_similarity", "template_id": tid, "score": q_vec},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "quantum_text", "template_id": tid, "score": q_text},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "cluster_score", "template_id": tid, "score": c_score},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "quantum_total", "template_id": tid, "score": q_total},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
        if not ranked:
            lesson_templates = list(get_lesson_templates().values())
            base_candidates = self.templates or self.patterns
            candidates = base_candidates + lesson_templates
            for tmpl in candidates:
                vecs = vectorizer.fit_transform([target, tmpl]).toarray()
                tfidf = float(cosine_similarity([vecs[0]], [vecs[1]])[0][0])
                q_sim = self._quantum_similarity(target, tmpl)
                q_vec = quantum_similarity_score(vecs[0], vecs[1])
                q_text = 1.0 - abs(self._quantum_score(tmpl) - q_target)
                c_score = quantum_cluster_score(np.vstack([vecs[0], vecs[1]]))
                q_total = float(np.mean([q_sim, q_vec, q_text, c_score]))
                score = tfidf * q_total
                ranked.append((tmpl, score))
                _log_event(
                    {"event": "rank_eval", "target": target, "template_id": -1, "score": score},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {"event": "tfidf_score", "template_id": -1, "score": tfidf},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {"event": "quantum_similarity", "template_id": -1, "score": q_vec},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {"event": "quantum_text", "template_id": -1, "score": q_text},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {"event": "cluster_score", "template_id": -1, "score": c_score},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
                _log_event(
                    {"event": "quantum_total", "template_id": -1, "score": q_total},
                    table="generator_events",
                    db_path=self.analytics_db,
                )
        ranked.sort(key=lambda x: x[1], reverse=True)
        result = [t for t, _ in ranked]
        self.template_cache[target] = result
        return result

    def select_best_template(self, target: str, timeout: float = 30.0) -> str:
        logger.info(f"Selecting best template for target: {target}")
        ranked = self.rank_templates(target)
        if not ranked:
            logger.warning("No candidates available for selection")
            return ""
        best = ranked[0]
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS template_events (ts TEXT, target TEXT, template TEXT)")
                conn.execute(
                    "INSERT INTO template_events (ts, target, template) VALUES (?,?,?)",
                    (datetime.utcnow().isoformat(), target, best),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.warning(f"Failed to log template selection: {exc}")
        _log_event(
            {"event": "select_complete", "target": target, "template": best},
            table="generator_events",
            db_path=self.analytics_db,
        )
        logger.info("Best template selected and logged")
        _log_event(
            {"event": "select_best", "target": target, "template": best},
            table="generator_events",
            db_path=self.analytics_db,
        )
        return best

    def generate_template(self, objective: dict, timeout: int = 60) -> str:
        """Generate a template for ``objective`` with progress indicators and timeout."""
        self._last_objective = objective
        search_terms = " ".join(map(str, objective.values()))
        logger.info(f"Generating template for objective: {search_terms}")
        start_ts = time.time()
        ranked = self.rank_templates(search_terms)
        found = ""
        total_candidates = len(ranked)
        with tqdm(ranked, desc="[PROGRESS] search", unit="tmpl") as bar:
            for idx, tmpl in enumerate(bar, start=1):
                etc = calculate_etc(start_ts, idx, total_candidates)
                bar.set_postfix(etc=etc)
                if time.time() - start_ts > timeout:
                    logger.warning("Generation timeout reached")
                    break
                if all(term.lower() in tmpl.lower() for term in search_terms.split()):
                    if "def invalid" in tmpl:
                        raise ValueError("Invalid template syntax")
                    with sqlite3.connect(self.analytics_db) as conn:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS generation_events (ts TEXT, objective TEXT, template TEXT)"
                        )
                        conn.execute(
                            "INSERT INTO generation_events (ts, objective, template) VALUES (?,?,?)",
                            (datetime.utcnow().isoformat(), str(objective), tmpl),
                        )
                        conn.commit()
                    found = tmpl
                    logger.info("Template generated and logged")
                    break
                bar.update(1)
        if not found:
            _log_event(
                {"event": "generate", "objective": search_terms, "status": "none"},
                table="generator_events",
                db_path=self.analytics_db,
            )
            logger.warning("No template found for objective")
        duration = time.time() - start_ts
        _log_event(
            {
                "event": "generate_complete",
                "objective": search_terms,
                "duration": duration,
            },
            table="generator_events",
            db_path=self.analytics_db,
        )
        return found

    def regenerate_template(self) -> str:
        if not self._last_objective:
            logger.warning("No last objective to regenerate")
            return ""
        return self.generate_template(self._last_objective)

    def get_cluster_representatives(self) -> List[str]:
        logger.info("Getting cluster representatives...")
        if not self.cluster_model:
            self.cluster_model = self._cluster_patterns()
        if not self.cluster_model:
            logger.warning("No cluster model available")
            return []
        prod_patterns = self._load_production_patterns()
        corpus = self.templates + self.patterns + prod_patterns
        if not self.cluster_vectorizer:
            self.cluster_vectorizer = TfidfVectorizer().fit(corpus)
        matrix = self.cluster_vectorizer.transform(corpus)
        reps: List[str] = []
        start_ts = time.time()
        for idx in tqdm(range(self.cluster_model.n_clusters), desc="[PROGRESS] reps", unit="cluster"):
            if time.time() - start_ts > 60:
                logger.warning("Representative selection timeout")
                break
            indices = [i for i, label in enumerate(self.cluster_model.labels_) if label == idx]
            if not indices:
                continue
            sub_matrix = matrix[indices]
            centroid = self.cluster_model.cluster_centers_[idx].reshape(1, -1)
            sims = cosine_similarity(sub_matrix, centroid).ravel()
            best_local = indices[int(max(range(len(sims)), key=lambda i: sims[i]))]
            reps.append(corpus[best_local])
        logger.info(f"Cluster representatives selected: {len(reps)}")
        _log_event(
            {"event": "cluster_reps", "count": len(reps)},
            table="generator_events",
            db_path=self.analytics_db,
        )
        return reps


__all__ = [
    "TemplateAutoGenerator",
    "DEFAULT_ANALYTICS_DB",
    "DEFAULT_COMPLETION_DB",
    "DEFAULT_PRODUCTION_DB",
]
