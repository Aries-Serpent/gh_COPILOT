from __future__ import annotations

import logging
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# Quantum demo import (placeholder for quantum-inspired scoring)
try:
    from quantum_algorithm_library_expansion import demo_quantum_fourier_transform
except ImportError:
    def demo_quantum_fourier_transform():
        # Fallback: return a normalized vector
        return np.ones(8) / np.sqrt(8)

DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")

LOGS_DIR = Path("logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"auto_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
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
    """Generate and cluster templates loaded from SQLite databases with visual processing indicators."""

    analytics_db: Path = DEFAULT_ANALYTICS_DB
    completion_db: Path = DEFAULT_COMPLETION_DB

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._log_event("init_start", {"timestamp": datetime.utcnow().isoformat()})
        start_time = datetime.now()
        logger.info("PROCESS STARTED: TemplateAutoGenerator Initialization")
        logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
        validate_no_recursive_folders()
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_model = self._cluster_patterns()
        self._last_objective: Dict[str, Any] | None = None
        duration = (datetime.now() - start_time).total_seconds()
        self._log_event("init_complete", {"duration": duration})
        logger.info(f"Initialization completed in {duration:.2f}s")

    def _load_patterns(self) -> List[str]:
        logger.info("Loading patterns from analytics DB...")
        patterns = []
        if self.analytics_db.exists():
            with sqlite3.connect(self.analytics_db) as conn:
                try:
                    cur = conn.execute(
                        "SELECT replacement_template FROM ml_pattern_optimization"
                    )
                    patterns = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading patterns: {exc}")
        logger.info(f"Loaded {len(patterns)} patterns")
        return patterns

    def _load_templates(self) -> List[str]:
        logger.info("Loading templates from completion DB...")
        templates = []
        if self.completion_db.exists():
            with sqlite3.connect(self.completion_db) as conn:
                try:
                    cur = conn.execute("SELECT template_content FROM templates")
                    templates = [row[0] for row in cur.fetchall()]
                except sqlite3.Error as exc:
                    logger.error(f"Error loading templates: {exc}")
        logger.info(f"Loaded {len(templates)} templates")
        return templates

    def _quantum_score(self, text: str) -> float:
        """Return a quantum-inspired score for ``text``."""
        vec = np.array(demo_quantum_fourier_transform())
        baseline = np.ones_like(vec) / np.sqrt(len(vec))
        return float(abs(np.dot(vec, baseline.conj())))

    def _cluster_patterns(self) -> KMeans | None:
        logger.info("Clustering patterns and templates...")
        corpus = self.templates + self.patterns
        if not corpus:
            logger.warning("No corpus to cluster")
            return None
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(corpus)
        n_clusters = min(len(corpus), 2)
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
        start = time.time()
        with tqdm(total=1, desc="clustering", unit="step") as pbar:
            model.fit(matrix)
            pbar.update(1)
        logger.info(f"Clustered {len(corpus)} items into {n_clusters} groups in {(time.time()-start):.2f}s")
        return model

    def objective_similarity(self, a: str, b: str) -> float:
        vectorizer = TfidfVectorizer().fit([a, b])
        vecs = vectorizer.transform([a, b])
        return float(cosine_similarity(vecs[0], vecs[1])[0][0])

    def select_best_template(self, target: str) -> str:
        logger.info(f"Selecting best template for target: {target}")
        candidates = self.templates if self.templates else self.patterns
        if not candidates:
            logger.warning("No candidates available for selection")
            return ""
        scores = [
            self.objective_similarity(target, c) + self._quantum_score(c)
            for c in candidates
        ]
        best_idx = int(max(range(len(scores)), key=scores.__getitem__))
        best = candidates[best_idx]
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS template_events (ts TEXT, target TEXT, template TEXT)",
                )
                conn.execute(
                    "INSERT INTO template_events (ts, target, template) VALUES (?,?,?)",
                    (datetime.utcnow().isoformat(), target, best),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.warning(f"Failed to log template selection: {exc}")
        logger.info("Best template selected and logged")
        return best

    def generate_template(self, objective: dict) -> str:
        self._last_objective = objective
        search_terms = " ".join(map(str, objective.values()))
        logger.info(f"Generating template for objective: {search_terms}")
        start = datetime.utcnow()
        found = ""
        with tqdm(self.templates + self.patterns, desc="[PROGRESS] search", unit="tmpl") as bar:
            for tmpl in bar:
                if all(term.lower() in tmpl.lower() for term in search_terms.split()):
                    if "def invalid" in tmpl:
                        raise ValueError("Invalid template syntax")
                    with sqlite3.connect(self.analytics_db) as conn:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS generation_events (ts TEXT, objective TEXT, template TEXT)",
                        )
                        conn.execute(
                            "INSERT INTO generation_events (ts, objective, template) VALUES (?,?,?)",
                            (start.isoformat(), str(objective), tmpl),
                        )
                        conn.commit()
                    found = tmpl
                    logger.info("Template generated and logged")
                    break
                bar.update(1)
        if not found:
            self._log_event("generate", {"objective": search_terms, "status": "none"})
            logger.warning("No template found for objective")
        return found

    def regenerate_template(self) -> str:
        if not self._last_objective:
            logger.warning("No last objective to regenerate")
            return ""
        return self.generate_template(self._last_objective)

    def get_cluster_representatives(self) -> List[str]:
        logger.info("Getting cluster representatives...")
        if not self.cluster_model:
            logger.warning("No cluster model available")
            return []
        corpus = self.templates + self.patterns
        vectorizer = TfidfVectorizer().fit(corpus)
        matrix = vectorizer.transform(corpus)
        reps: List[str] = []
        for idx in tqdm(
            range(self.cluster_model.n_clusters), desc="[PROGRESS] reps", unit="cluster"
        ):
            indices = [
                i for i, label in enumerate(self.cluster_model.labels_) if label == idx
            ]
            if not indices:
                continue
            sub_matrix = matrix[indices]
            centroid = self.cluster_model.cluster_centers_[idx].reshape(1, -1)
            sims = cosine_similarity(sub_matrix, centroid).ravel()
            best_local = indices[int(max(range(len(sims)), key=lambda i: sims[i]))]
            reps.append(corpus[best_local])
        logger.info(f"Cluster representatives selected: {len(reps)}")
        return reps

    def _log_event(self, name: str, data: dict) -> None:
        """Log events to analytics DB and file."""
        try:
            self.analytics_db.parent.mkdir(exist_ok=True, parents=True)
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS generator_events (timestamp REAL, name TEXT, details TEXT)"
                )
                conn.execute(
                    "INSERT INTO generator_events (timestamp, name, details) VALUES (?,?,?)",
                    (time.time(), name, str(data)),
                )
                conn.commit()
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {name} | {data}\n")
        except Exception as exc:
            self.logger.debug("log_event failed: %s", exc)

__all__ = [
    "TemplateAutoGenerator",
    "DEFAULT_ANALYTICS_DB",
    "DEFAULT_COMPLETION_DB",
]
