from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

WORKSPACE_ENV_VAR = "GH_COPILOT_WORKSPACE"


class TemplateGenerator:
    """Generate content from templates stored in ``template.db``."""

    def __init__(self, workspace_root: str = ".") -> None:
        workspace = os.getenv(WORKSPACE_ENV_VAR, workspace_root)
        self.workspace_root = Path(workspace)
        self.db_path = self.workspace_root / "databases" / "template.db"

    def _fetch_template(self, pattern: str) -> str:
        like_pattern = pattern.replace("*", "%")
        query = (
            "SELECT template_content FROM templates "
            "WHERE template_name LIKE ? ORDER BY id LIMIT 1"
        )
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(query, (like_pattern,))
            row = cur.fetchone()
        if row is None:
            raise ValueError(f"No template matching '{pattern}'")
        return row[0]

    def generate_from_pattern(self, pattern: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Return generated text using the first template matching ``pattern``."""
        template_content = self._fetch_template(pattern)
        try:
            return template_content.format(**(context or {}))
        except KeyError as exc:
            missing = exc.args[0]
            logger.error("Missing placeholder '%s' in context", missing)
            raise
