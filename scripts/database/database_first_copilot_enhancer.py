#!/usr/bin/env python3
"""Database-First Copilot Enhancer."""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from template_engine.objective_similarity_scorer import compute_similarity_scores


class DatabaseFirstCopilotEnhancer:
    """Provide database-first code generation helpers."""

    def __init__(self, workspace_path: str = ".") -> None:
        self.workspace = Path(workspace_path)
        self.production_db = self.workspace / "databases" / "production.db"
        self.analytics_db = self.workspace / "databases" / "analytics.db"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.template_engine = self._initialize_template_engine()
        self._validate_environment_compliance()

    def _validate_environment_compliance(self) -> None:
        """Ensure no forbidden backup folders exist inside the workspace."""
        if any(self.workspace.glob("**/*backup*")):
            raise RuntimeError("Forbidden backup folder detected")
        backup_root = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if backup_root:
            backup_path = Path(backup_root).resolve()
            try:
                backup_path.relative_to(self.workspace.resolve())
                raise RuntimeError("Backup root must be outside the workspace")
            except ValueError:
                pass

    def _initialize_template_engine(self) -> Any:
        """Load templates from database or filesystem with fallback."""

        def load_db_templates() -> dict[str, str]:
            templates: dict[str, str] = {}
            if self.production_db.exists():
                validate_enterprise_operation(str(self.production_db))
                try:
                    with sqlite3.connect(self.production_db) as conn:
                        validate_enterprise_operation(str(self.production_db))
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS templates (name TEXT PRIMARY KEY, template_content TEXT)"
                        )
                        cur = conn.execute("SELECT name, template_content FROM templates")
                        templates = {row[0]: row[1] for row in cur.fetchall()}
                except sqlite3.Error as exc:
                    self.logger.warning("Error loading templates from %s: %s", self.production_db, exc)
            return templates

        def load_fs_templates() -> dict[str, str]:
            templates: dict[str, str] = {}
            tpl_dir = self.workspace / "templates"
            if tpl_dir.exists():
                validate_enterprise_operation(str(tpl_dir))
                for path in tpl_dir.glob("*.tmpl"):
                    try:
                        templates[path.stem] = path.read_text(encoding="utf-8")
                    except OSError as exc:
                        self.logger.warning("Could not read %s: %s", path, exc)
            return templates

        templates = load_db_templates()
        if templates:
            templates.update(load_fs_templates())
        else:
            templates = load_fs_templates()

        try:
            from template_engine.pattern_templates import get_named_templates

            templates.update(get_named_templates())
        except Exception as exc:  # pragma: no cover - log only
            self.logger.warning("Failed to load pattern templates: %s", exc)

        default_template = templates.get("default")

        def engine(name: str) -> str:
            tmpl = templates.get(name)
            if tmpl is None:
                tmpl = default_template or templates.get("fallback") or f"# Template for {name} in {{workspace}}"
            return tmpl

        return engine

    def _query_database_solutions(self, objective: str) -> List[Tuple[str, float]]:
        """Return code snippets and scores ranked by similarity to ``objective``."""
        if not self.production_db.exists():
            return []
        validate_enterprise_operation(str(self.production_db))
        validate_enterprise_operation(str(self.analytics_db))
        scores: List[Tuple[int, float]] = compute_similarity_scores(
            objective, production_db=self.production_db, analytics_db=self.analytics_db
        )
        results: List[Tuple[str, float]] = []
        validate_enterprise_operation(str(self.production_db))
        with sqlite3.connect(self.production_db) as conn:
            validate_enterprise_operation(str(self.production_db))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS similarity_scores (objective TEXT, template_id INTEGER, score REAL)"
            )
            for tid, score in scores:
                conn.execute(
                    "INSERT INTO similarity_scores (objective, template_id, score) VALUES (?,?,?)",
                    (objective, tid, score),
                )
            conn.commit()
            for tid, score in sorted(scores, key=lambda s: s[1], reverse=True):
                row = conn.execute(
                    "SELECT template_code FROM code_templates WHERE id=?", (tid,)
                ).fetchone()
                if row:
                    results.append((row[0], score))
        return results

    def _find_template_matches(self, objective: str) -> str:
        return self.template_engine(objective)

    def _adapt_to_current_environment(self, template: str) -> str:
        """Inject environment specific values into ``template``."""
        return template.replace("{workspace}", str(self.workspace))

    def _calculate_confidence(self, solutions: List[Tuple[str, float]]) -> float:
        """Return confidence based on highest similarity score."""
        if not solutions:
            return 0.0
        max_score = max(score for _code, score in solutions)
        return float(max(0.0, min(1.0, max_score)))

    def query_before_filesystem(self, objective: str) -> Dict[str, Any]:
        """Query database before using filesystem templates."""
        scored = self._query_database_solutions(objective)
        template = self._find_template_matches(objective)
        adapted = self._adapt_to_current_environment(template)
        codes = [code for code, _ in scored]
        return {
            "database_solutions": codes,
            "template_code": adapted,
            "confidence_score": self._calculate_confidence(scored),
            "integration_ready": True,
        }

    def generate_integration_ready_code(self, objective: str) -> str:
        """Generate code using progress indicators."""
        with tqdm(total=3, desc="generate", unit="step") as bar:
            bar.update(1)
            result = self.query_before_filesystem(objective)
            bar.update(1)
            code = result["template_code"]
            bar.update(1)
        duration = float(bar.format_dict.get("elapsed", 0))
        self.logger.info("Generated code for %s in %.2fs", objective, duration)
        template_name = objective
        validate_enterprise_operation(str(self.production_db))
        with sqlite3.connect(self.production_db) as conn:
            validate_enterprise_operation(str(self.production_db))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS generated_solutions (objective TEXT, template_name TEXT, code TEXT)"
            )
            conn.execute(
                "INSERT INTO generated_solutions (objective, template_name, code) VALUES (?,?,?)",
                (objective, template_name, code),
            )
            conn.commit()
        validate_enterprise_operation(str(self.analytics_db))
        with sqlite3.connect(self.analytics_db) as conn:
            validate_enterprise_operation(str(self.analytics_db))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS generation_log (objective TEXT, duration REAL, ts TEXT)"
            )
            conn.execute(
                "INSERT INTO generation_log (objective, duration, ts) VALUES (?,?,?)",
                (objective, duration, datetime.utcnow().isoformat()),
            )
            conn.commit()
        return code
