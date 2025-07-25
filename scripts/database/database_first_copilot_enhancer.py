#!/usr/bin/env python3
"""Database-First Copilot Enhancer."""

from __future__ import annotations

import logging
import os
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm


class DatabaseFirstCopilotEnhancer:
    """Provide database-first code generation helpers."""

    def __init__(self, workspace_path: str = ".") -> None:
        self.workspace = Path(workspace_path)
        self.production_db = self.workspace / "databases" / "production.db"
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
                try:
                    with sqlite3.connect(self.production_db) as conn:
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

        default_template = templates.get("default")

        def engine(name: str) -> str:
            tmpl = templates.get(name)
            if tmpl is None:
                tmpl = default_template or templates.get("fallback") or f"# Template for {name} in {{workspace}}"
            return tmpl

        return engine

    def _query_database_solutions(self, objective: str) -> List[str]:
        """Return code snippets matching ``objective`` from ``production.db``."""
        if not self.production_db.exists():
            return []
        with sqlite3.connect(self.production_db) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS solutions (objective TEXT, code TEXT)")
            cur.execute("SELECT objective, code FROM solutions")
            matches: List[tuple[float, str]] = []
            for obj, code in cur.fetchall():
                score = SequenceMatcher(None, objective, obj).ratio()
                if score >= 0.5:
                    matches.append((score, code))
            matches.sort(key=lambda x: x[0], reverse=True)
            return [code for _, code in matches]

    def _find_template_matches(self, objective: str) -> str:
        return self.template_engine(objective)

    def _adapt_to_current_environment(self, template: str) -> str:
        """Inject environment specific values into ``template``."""
        return template.replace("{workspace}", str(self.workspace))

    def _calculate_confidence(self, solutions: List[str]) -> float:
        if not solutions:
            return 0.0
        # simplistic confidence based on number of solutions
        return min(1.0, len(solutions) / 5)

    def query_before_filesystem(self, objective: str) -> Dict[str, Any]:
        """Query database before using filesystem templates."""
        solutions = self._query_database_solutions(objective)
        template = self._find_template_matches(objective)
        adapted = self._adapt_to_current_environment(template)
        return {
            "database_solutions": solutions,
            "template_code": adapted,
            "confidence_score": self._calculate_confidence(solutions),
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
        duration = bar.format_dict.get("elapsed", 0)
        self.logger.info("Generated code for %s in %.2fs", objective, duration)
        return code
