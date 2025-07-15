#!/usr/bin/env python3
"""Consolidate the documentation database and generate feature matrix."""
<<<<<<< HEAD

from __future__ import annotations

import csv
import json
=======
from __future__ import annotations

import csv
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
import os
import re
import sqlite3
import uuid
<<<<<<< HEAD
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

from utils.log_utils import DEFAULT_ANALYTICS_DB, insert_event

CLEANUP_SQL = "DELETE FROM enterprise_documentation WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"
=======
from pathlib import Path
from typing import Iterable, Tuple
import logging

CLEANUP_SQL = (
    "DELETE FROM enterprise_documentation "
    "WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"
)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
DEDUPE_SQL = (
    "DELETE FROM enterprise_documentation WHERE rowid NOT IN ("
    "SELECT MIN(rowid) FROM enterprise_documentation GROUP BY title)"
)

WORKSPACE_ENV_VAR = "GH_COPILOT_WORKSPACE"
<<<<<<< HEAD
DOC_DB_ENV_VAR = "DOCUMENTATION_DB_PATH"
=======

# SQL statements for cleanup operations
CLEANUP_SQL = (
    "DELETE FROM enterprise_documentation "
    "WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"
)
DEDUPE_SQL = (
    "DELETE FROM enterprise_documentation WHERE rowid NOT IN ("
    "SELECT MIN(rowid) FROM enterprise_documentation GROUP BY title"
    ")"
)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def get_workspace() -> Path:
    """Return workspace root from environment or repo root."""
    root = Path(__file__).resolve().parents[1]
    workspace = Path(os.getenv(WORKSPACE_ENV_VAR, root))
    return workspace


<<<<<<< HEAD
def get_doc_db_path(workspace: Path) -> Path:
    """Return documentation database path from environment or workspace."""
    env_path = os.getenv(DOC_DB_ENV_VAR)
    if env_path:
        return Path(env_path)
    return workspace / "archives" / "documentation.db"


def cleanup_database(db_path: Path) -> None:
    """Remove backup and duplicate documentation entries."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

=======
def cleanup_database(db_path: Path) -> None:
    """Remove backup and duplicate documentation entries."""
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(CLEANUP_SQL)
        cur.execute(DEDUPE_SQL)
        conn.commit()


<<<<<<< HEAD
def ensure_registry_table(db_path: Path) -> None:
    """Create template registry if missing."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS template_registry (
                template_id TEXT PRIMARY KEY,
                doc_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
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
<<<<<<< HEAD
            conn.execute(
                "INSERT OR REPLACE INTO template_registry (template_id, doc_type, created_at) VALUES (?, ?, ?)",
                (template_id, doc_type, datetime.utcnow().isoformat()),
            )
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
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
<<<<<<< HEAD
    path_json: Path,
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    implemented: Iterable[str],
    planned: Iterable[str],
) -> None:
    """Write CSV and Markdown feature matrix."""
<<<<<<< HEAD
    rows = [(feat, "Implemented") for feat in implemented] + [(feat, "Planned") for feat in planned]
=======
    rows = [(feat, "Implemented") for feat in implemented] + [
        (feat, "Planned") for feat in planned
    ]
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    with path_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Feature", "Status"])
        writer.writerows(rows)

    md_lines = ["| Feature | Status |", "| --- | --- |"]
    md_lines += [f"| {feat} | {status} |" for feat, status in rows]
    path_md.write_text("\n".join(md_lines))

<<<<<<< HEAD
    path_json.write_text(json.dumps(rows, indent=2))

=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)

def generate_feature_matrix(workspace: Path) -> None:
    """Generate feature matrix from documentation README."""
    readme = workspace / "documentation" / "README.md"
    generated_dir = workspace / "documentation" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    csv_path = generated_dir / "feature_matrix.csv"
    md_path = generated_dir / "feature_matrix.md"
<<<<<<< HEAD
    json_path = generated_dir / "feature_matrix.json"
    implemented, planned = parse_features(readme)
    write_matrix(csv_path, md_path, json_path, implemented, planned)
    insert_event(
        {
            "db_name": str(csv_path),
            "details": f"feature_matrix:{len(implemented) + len(planned)}",
            "ts": datetime.utcnow().isoformat(),
        },
        table="audit_log",
        db_path=DEFAULT_ANALYTICS_DB,
        test_mode=False,
    )
=======
    implemented, planned = parse_features(readme)
    write_matrix(csv_path, md_path, implemented, planned)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def consolidate() -> None:
    """Run consolidation steps for documentation."""
    workspace = get_workspace()
<<<<<<< HEAD
    db_path = get_doc_db_path(workspace)
    ensure_registry_table(db_path)
    cleanup_database(db_path)
    populate_templates(db_path)
    generate_feature_matrix(workspace)
    insert_event(
        {
            "db_name": str(db_path),
            "details": "consolidate_complete",
            "ts": datetime.utcnow().isoformat(),
        },
        table="audit_log",
        db_path=DEFAULT_ANALYTICS_DB,
        test_mode=False,
    )
=======
    db_path = workspace / "databases" / "documentation.db"
    cleanup_database(db_path)
    populate_templates(db_path)
    generate_feature_matrix(workspace)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


if __name__ == "__main__":
    consolidate()
