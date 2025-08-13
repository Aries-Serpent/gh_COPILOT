from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .dao import GenerationDAO

@dataclass
class TemplateRecord:
    id: str
    path: str
    content: str

def _fetch_templates(db: Path, table: str) -> List[TemplateRecord]:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"SELECT id, path, content FROM {table}").fetchall()
        return [TemplateRecord(id=str(r["id"]), path=r["path"], content=r["content"]) for r in rows]
    finally:
        conn.close()

def _render_doc(t: TemplateRecord, params: Dict[str, str]) -> str:
    out = t.content
    for k, v in params.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out

def generate(kind: str, source_db: Path, out_dir: Path, analytics_db: Path, params: Dict[str,str]|None=None) -> list[Path]:
    params = params or {}
    dao = GenerationDAO(analytics_db)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if kind == "docs":
        templates = _fetch_templates(source_db, table="documentation_templates")
        for t in templates:
            target = out_dir / Path(t.path).with_suffix(".md").name
            content = _render_doc(t, params)
            target.write_text(content, encoding="utf-8")
            dao.log_event(kind="docs", source=str(source_db), target_path=str(target), template_id=t.id, inputs=params)
            written.append(target)
    elif kind == "scripts":
        templates = _fetch_templates(source_db, table="script_templates")
        for t in templates:
            target = out_dir / Path(t.path).with_suffix(".py").name
            target.write_text(t.content, encoding="utf-8")
            dao.log_event(kind="scripts", source=str(source_db), target_path=str(target), template_id=t.id, inputs=params)
            written.append(target)
    else:
        raise ValueError("kind must be 'docs' or 'scripts'")
    return written
