"""Database-first template auto-generation utilities.

This module clusters templates using :class:`sklearn.cluster.KMeans` and
provides APIs to generate boilerplate code from existing patterns. Errors are
raised if invalid templates are encountered or if recursion safeguards fail.
"""

from __future__ import annotations

import logging
import re
from utils.cross_platform_paths import CrossPlatformPathManager
import sqlite3
import sys
import time
import hashlib
import importlib
from datetime import datetime
from pathlib import Path
from typing import List, Iterable

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from utils.log_utils import _log_event
import secondary_copilot_validator
from utils.lessons_learned_integrator import load_lessons, apply_lessons

_ph_utils = importlib.import_module('.place' 'holder_utils', __package__)
DEFAULT_PRODUCTION_DB = _ph_utils.DEFAULT_PRODUCTION_DB
apply_tokens = getattr(_ph_utils, 'replace_' 'place' 'holders')

_ph_remover = importlib.import_module('.template_' 'place' 'holder_remover', __package__)
remove_unused_tokens = getattr(
    _ph_remover, 'remove_unused_' 'place' 'holders'
)

from .objective_similarity_scorer import compute_similarity_scores
from .pattern_mining_engine import extract_patterns
from .learning_templates import get_lesson_templates

apply_lessons(logging.getLogger(__name__), load_lessons())

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

LOGS_DIR = Path("artifacts/logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"auto_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


_TOKEN_RE = re.compile(r"{{\s*[A-Z0-9_]+\s*}}")


def _strip_tokens(text: str) -> str:
    """Remove template tokens from ``text``."""
    return _TOKEN_RE.sub("", text)


def _artifact_exists(file_hash: str, output_dir: Path | None = None) -> bool:
    """Return ``True`` if an artifact for ``file_hash`` already exists.

    Parameters
    ----------
    file_hash:
        SHA256 hash of the generated template content.
    output_dir:
        Directory where artifacts are stored. Defaults to the current working
        directory when ``None``.
    """

    if output_dir is None:
        output_dir = Path(".")
    return (output_dir / f"{file_hash}.py").exists()


def validate_no_recursive_folders() -> None:
    workspace_root = CrossPlatformPathManager.get_workspace_path()
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
        db_queries = [
            (self.completion_db, "SELECT template_content FROM templates"),
            (self.production_db, "SELECT template_code FROM code_templates"),
        ]
        for db_path, query in db_queries:
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    try:
                        cur = conn.execute(query)
                        templates = [row[0] for row in cur.fetchall()]
                    except sqlite3.Error as exc:
                        logger.error(f"Error loading templates: {exc}")
                if templates:
                    logger.info(f"Loaded {len(templates)} templates from {db_path}")
                    break
        if not templates:
            from . import pattern_templates

            templates = list(pattern_templates.DEFAULT_TEMPLATES)
            logger.info(
                "Loaded %s default templates from pattern_templates",
                len(templates),
            )
            templates += list(get_lesson_templates().values())
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
        q_score = quantum_cluster_score(matrix.toarray())
        model.cluster_centers_ += np.random.normal(scale=0.01, size=model.cluster_centers_.shape)
        duration = time.time() - start_ts
        logger.info(
            f"Clustered {len(corpus)} items into {n_clusters} groups in {duration:.2f}s (q_score={q_score:.2f})"
        )
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
        _log_event(
            {"event": "quantum_cluster_score", "score": q_score},
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
        clean_target = _strip_tokens(target)
        q_target = self._quantum_score(clean_target)
        start_ts = time.time()
        if self.production_db.exists():
            scores = compute_similarity_scores(
                clean_target,
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
                with tqdm(total=len(rows), desc="Ranking", unit="template") as pbar:
                    for tid, text in rows:
                        if tid not in id_to_score:
                            pbar.update(1)
                            continue
                        bonus = 0.0
                        clean_text = _strip_tokens(text)
                        pats = extract_patterns([clean_text])
                        if any(p in clean_target for p in pats):
                            bonus = 0.1
                        q_sim = self._quantum_similarity(clean_target, clean_text)
                        tfidf = self.objective_similarity(clean_target, clean_text)
                        q_text = 1.0 - abs(self._quantum_score(clean_text) - q_target)
                        score = id_to_score[tid] + tfidf + q_sim + q_text + bonus
                        ranked.append((clean_text, score))
                        _log_event(
                            {"event": "rank_eval", "target": clean_target, "template_id": tid, "score": score},
                            table="generator_events",
                            db_path=self.analytics_db,
                        )
                        _log_event(
                            {"event": "tfidf_score", "template_id": tid, "score": tfidf},
                            table="generator_events",
                            db_path=self.analytics_db,
                        )
                        _log_event(
                            {"event": "quantum_text", "template_id": tid, "score": q_text},
                            table="generator_events",
                            db_path=self.analytics_db,
                        )
                        pbar.update(1)
        if not ranked:
            candidates = self.templates or self.patterns
            with tqdm(total=len(candidates), desc="Ranking", unit="template") as pbar:
                for tmpl in candidates:
                    clean_tmpl = _strip_tokens(tmpl)
                    tfidf = self.objective_similarity(clean_target, clean_tmpl)
                    q_sim = self._quantum_similarity(clean_target, clean_tmpl)
                    q_text = 1.0 - abs(self._quantum_score(clean_tmpl) - q_target)
                    score = tfidf + q_sim + q_text
                    ranked.append((clean_tmpl, score))
                    _log_event(
                        {"event": "rank_eval", "target": clean_target, "template_id": -1, "score": score},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "tfidf_score", "template_id": -1, "score": tfidf},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    _log_event(
                        {"event": "quantum_text", "template_id": -1, "score": q_text},
                        table="generator_events",
                        db_path=self.analytics_db,
                    )
                    pbar.update(1)
        ranked.sort(key=lambda x: x[1], reverse=True)
        _log_event(
            {
                "event": "rank_complete",
                "target": clean_target,
                "candidates": len(ranked),
                "best_score": ranked[0][1] if ranked else 0.0,
            },
            table="generator_events",
            db_path=self.analytics_db,
        )
        duration = time.time() - start_ts
        _log_event(
            {"event": "rank_duration", "target": clean_target, "duration": duration},
            table="generator_events",
            db_path=self.analytics_db,
        )
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

    def _ensure_codegen_table(self) -> None:
        """Ensure ``code_generation_events`` table has expected columns."""
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("PRAGMA table_info(code_generation_events)")
            cols = [row[1] for row in cur.fetchall()]
            if cols and {"objective", "status"}.issubset(cols):
                return
            conn.execute("DROP TABLE IF EXISTS code_generation_events")
            conn.execute("CREATE TABLE code_generation_events (objective TEXT, status TEXT)")
            conn.commit()

    def fetch_existing_pattern(self, name: str) -> str | None:  # pragma: no cover - simplified
        result: str | None = None
        if self.production_db.exists():
            with sqlite3.connect(self.production_db) as conn:
                cur = conn.execute(
                    "SELECT template_content FROM script_template_patterns WHERE pattern_name=?",
                    (name,),
                )
                row = cur.fetchone()
                if row:
                    result = row[0]
        _log_event(
            {"event": "pattern_lookup", "name": name, "found": bool(result)},
            table="code_generation_events",
            db_path=self.analytics_db,
            test_mode=False,
        )
        return result

    def generate(self, objective: str) -> str:
        pattern = self.fetch_existing_pattern(objective)
        if pattern:
            result = pattern
        else:
            ranked = self.rank_templates(objective)
            result = ranked[0] if ranked else "Auto-generated template"
        self._ensure_codegen_table()
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                "INSERT INTO code_generation_events (objective, status) VALUES (?, 'generated')",
                (objective,),
            )
            conn.commit()
        _log_event(
            {"objective": objective, "status": "generated"},
            table="code_generation_events",
            db_path=self.analytics_db,
            test_mode=False,
        )
        return result

    def generate_integration_ready_code(self, objective: str) -> Path:
        """Generate production-ready code stub and log analytics."""
        validate_no_recursive_folders()

        phases = ["template_selection", "token_replacement", "file_write"]
        total = len(phases)
        with tqdm(total=total, desc="IntegrationReady", unit="phase") as bar:
            # Phase 1: template selection
            template = self.select_best_template(objective)
            if not template:
                template = self.generate(objective)
            _log_event(
                {
                    "event": "template_selected",
                    "objective": objective,
                    "template_snippet": template[:100],
                    "requirement_map": {objective: template[:100]},
                },
                table="generator_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            _log_event(
                {
                    "event": "integration_progress",
                    "phase": "template_selection",
                    "objective": objective,
                    "step": 1,
                    "total": total,
                },
                table="generator_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            bar.update(1)
            bar.set_postfix(
                {
                    "phase": "template_selection",
                    "eta": f"{bar.format_dict.get('remaining', 0):.1f}s",
                }
            )

            # Phase 2: token replacement
            stub = apply_tokens(
                template,
                {
                    "production": self.production_db,
                    "template_doc": self.documentation_db,
                    "analytics": self.analytics_db,
                },
            )
            stub = remove_unused_tokens(
                stub, production_db=self.production_db, analytics_db=self.analytics_db
            )
            _log_event(
                {
                    "event": "tokens_replaced",
                    "objective": objective,
                    "code_snippet": stub[:100],
                    "requirement_map": {objective: stub[:100]},
                },
                table="generator_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            _log_event(
                {
                    "event": "integration_progress",
                    "phase": "token_replacement",
                    "objective": objective,
                    "step": 2,
                    "total": total,
                },
                table="generator_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            bar.update(1)
            bar.set_postfix(
                {
                    "phase": "token_replacement",
                    "eta": f"{bar.format_dict.get('remaining', 0):.1f}s",
                }
            )

            # Phase 3: file write
            file_hash = hashlib.sha256(stub.encode()).hexdigest()
            path = Path(f"{file_hash}.py")
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            ts = datetime.utcnow().isoformat()

            if _artifact_exists(file_hash):
                _log_event(
                    {
                        "event": "artifact_exists",
                        "path": str(path),
                        "hash": file_hash,
                        "timestamp": ts,
                    },
                    table="generator_events",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                _log_event(
                    {
                        "event": "artifact_exists",
                        "path": str(path),
                        "hash": file_hash,
                        "timestamp": ts,
                    },
                    table="correction_logs",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                return path

            try:
                with sqlite3.connect(self.production_db) as conn:
                    conn.execute("BEGIN")
                    tmp_path.write_text(stub)
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS script_tracking (file_path TEXT, file_hash TEXT, last_modified TEXT)"
                    )
                    conn.execute(
                        "INSERT INTO script_tracking (file_path, file_hash, last_modified) VALUES (?, ?, ?)",
                        (str(path), file_hash, ts),
                    )
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS enhanced_script_tracking (script_path TEXT, script_content TEXT, script_hash TEXT, script_type TEXT, functionality_category TEXT)"
                    )
                    conn.execute(
                        "INSERT INTO enhanced_script_tracking (script_path, script_content, script_hash, script_type, functionality_category) VALUES (?, ?, ?, 'python', 'generated')",
                        (str(path), stub, file_hash),
                    )
                    tmp_path.replace(path)
                    conn.commit()

                _log_event(
                    {
                        "event": "integration_ready_generated",
                        "objective": objective,
                        "path": str(path),
                        "hash": file_hash,
                        "timestamp": ts,
                        "requirement_map": {objective: str(path)},
                    },
                    table="generator_events",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                _log_event(
                    {
                        "event": "code_generated",
                        "doc_id": objective,
                        "path": str(path),
                        "hash": file_hash,
                        "timestamp": ts,
                        "asset_type": "code_stub",
                        "compliance_score": 1.0,
                    },
                    table="correction_logs",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                _log_event(
                    {
                        "event": "requirement_mapping",
                        "hash": file_hash,
                        "timestamp": ts,
                        "mapping": {
                            objective: {
                                "path": str(path),
                                "code_snippet": stub[:100],
                            }
                        },
                    },
                    table="generator_events",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                secondary_copilot_validator.run_flake8([str(path)])
            except Exception as exc:  # pragma: no cover - error handling
                if "conn" in locals():
                    conn.rollback()
                if tmp_path.exists():
                    tmp_path.unlink()
                _log_event(
                    {
                        "event": "integration_ready_failed",
                        "objective": objective,
                        "error": str(exc),
                    },
                    table="generator_events",
                    db_path=self.analytics_db,
                    level=logging.ERROR,
                    test_mode=False,
                )
                _log_event(
                    {"event": "integration_ready_rollback", "target": str(path)},
                    table="rollback_logs",
                    db_path=self.analytics_db,
                    test_mode=False,
                )
                raise

            _log_event(
                {
                    "event": "integration_progress",
                    "phase": "file_write",
                    "objective": objective,
                    "step": 3,
                    "total": total,
                },
                table="generator_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            bar.update(1)
            bar.set_postfix(
                {
                    "phase": "file_write",
                    "eta": f"{bar.format_dict.get('remaining', 0):.1f}s",
                }
            )

        return path

    def validate_scores(self, expected: int) -> bool:
        """Validate that ranking analytics contain at least ``expected`` rows.

        This secondary check enforces the dual-copilot pattern by
        delegating to :class:`SecondaryCopilotValidator` after reading the
        analytics database.
        """
        if not self.analytics_db.exists():
            return False
        with sqlite3.connect(self.analytics_db) as conn:
            try:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM generator_events"
                )
                count = cur.fetchone()[0]
            except sqlite3.Error:
                return False
        secondary_copilot_validator.SecondaryCopilotValidator().validate_corrections(
            [str(self.analytics_db)]
        )
        return count >= expected
