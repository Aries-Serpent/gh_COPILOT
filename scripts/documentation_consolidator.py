#!/usr/bin/env python3
"""Consolidate the documentation database and generate feature matrix."""
from __future__ import annotations

import csv
import os
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Iterable, Tuple

WORKSPACE_ENV_VAR = "GH_COPILOT_WORKSPACE"

# SQL statements used for cleanup
CLEANUP_SQL = "DELETE FROM enterprise_documentation WHERE doc_type='BACKUP_LOG'"
DEDUPE_SQL = (
    "DELETE FROM enterprise_documentation WHERE rowid NOT IN ("
    "SELECT MIN(rowid) FROM enterprise_documentation GROUP BY title)"
)


def get_workspace() -> Path:
    """Return workspace root from environment or repo root."""
    root = Path(__file__).resolve().parents[1]
    workspace = Path(os.getenv(WORKSPACE_ENV_VAR, root))
    return workspace


def cleanup_database(db_path: Path) -> None:
    """Remove backup and duplicate documentation entries."""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(CLEANUP_SQL)
        cur.execute(DEDUPE_SQL)
        conn.commit()


def extract_headings(text: str) -> str:
    """Return newline-separated Markdown headings from ``text``."""
    headings: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            headings.append(line.strip())
    return "\n".join(headings)


def populate_templates(db_path: Path) -> None:
    """Populate template table using patterns from documentation."""
    query = "SELECT DISTINCT doc_type, content FROM enterprise_documentation"
    templates: dict[str, str] = {}
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(query)
        for doc_type, content in cur.fetchall():
            if doc_type in templates:
                continue
            templates[doc_type] = extract_headings(content)

        for doc_type, pattern in templates.items():
            if not pattern:
                continue
            template_id = str(uuid.uuid4())
            template_name = f"{doc_type.lower()}_template"
            conn.execute(
                "INSERT INTO documentation_templates"
                " (template_id, template_name, template_type, template_content)"
                " VALUES (?, ?, ?, ?)",
                (template_id, template_name, doc_type, pattern),
            )
        conn.commit()


def parse_features(readme: Path) -> Tuple[list[str], list[str]]:
    """Return lists of implemented and planned features from a README."""
    implemented: list[str] = []
    planned: list[str] = []
    in_planned = False
    header_re = re.compile(r"^#+\s*(.*)")
    with readme.open() as f:
        for line in f:
            stripped = line.strip()
            m = header_re.match(stripped)
            if m:
                heading = m.group(1).lower()
                if "planned" in heading:
                    in_planned = True
                else:
                    in_planned = False
            elif stripped.startswith("-"):
                feature = stripped.lstrip("- ").strip()
                if in_planned or "concept only" in feature.lower() or "planned" in feature.lower():
                    planned.append(feature)
                else:
                    implemented.append(feature)
    return implemented, planned


def write_matrix(
    path_csv: Path,
    path_md: Path,
    implemented: Iterable[str],
    planned: Iterable[str],
) -> None:
    """Write CSV and Markdown feature matrix."""
    rows = [(feat, "Implemented") for feat in implemented] + [
        (feat, "Planned") for feat in planned
    ]
    with path_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Feature", "Status"])
        writer.writerows(rows)

    md_lines = ["| Feature | Status |", "| --- | --- |"]
    md_lines += [f"| {feat} | {status} |" for feat, status in rows]
    path_md.write_text("\n".join(md_lines))


def generate_feature_matrix(workspace: Path) -> None:
    """Generate feature matrix from documentation README."""
    readme = workspace / "documentation" / "README.md"
    generated_dir = workspace / "documentation" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    csv_path = generated_dir / "feature_matrix.csv"
    md_path = generated_dir / "feature_matrix.md"
    implemented, planned = parse_features(readme)
    write_matrix(csv_path, md_path, implemented, planned)


def consolidate() -> None:
    """Run consolidation steps for documentation."""
    workspace = get_workspace()
    db_path = workspace / "databases" / "documentation.db"
    cleanup_database(db_path)
    populate_templates(db_path)
    generate_feature_matrix(workspace)


if __name__ == "__main__":
    consolidate()
