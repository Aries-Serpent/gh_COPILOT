from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict


class TemplateGenerator:
    """Simple template generator for tests."""

    def __init__(self, workspace_path: str) -> None:
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / "databases" / "template.db"

    def generate_from_pattern(self, pattern: str, variables: Dict[str, str]) -> str:
        if not self.db_path.exists():
            return ""
        query = pattern.replace("*", "%")
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT template_content FROM templates WHERE template_name LIKE ?",
                (query,),
            )
            row = cur.fetchone()
        if row:
            return row[0].format(**variables)
        return ""
