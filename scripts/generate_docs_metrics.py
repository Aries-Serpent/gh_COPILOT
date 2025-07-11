#!/usr/bin/env python3
"""Generate documentation metrics in README files."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "production.db"
README_PATHS = [
    ROOT / "README.md",
    ROOT / "documentation" / "generated" / "README.md",
    ROOT / "documentation" / "generated" / "SYSTEM_STATUS.md",
]
DATABASE_LIST = ROOT / "documentation" / "DATABASE_LIST.md"


def get_metrics() -> dict[str, int]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM enterprise_script_tracking")
    scripts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM script_template_patterns")
    templates = cur.fetchone()[0]
    conn.close()
    with DATABASE_LIST.open() as f:
        databases = sum(
            1
            for line in f
            if line.strip().startswith("- ") and line.strip().endswith(".db")
        )
    return {"scripts": scripts, "templates": templates, "databases": databases}


def update_file(path: Path, metrics: dict[str, int]) -> None:
    content = path.read_text()
    content = re.sub(
        r"(\*Generated from Enterprise Documentation Database on ).*?\*",
        lambda m: f"{m.group(1)}{datetime.now():%Y-%m-%d %H:%M:%S}*",
        content,
    )
    content = re.sub(
        r"(\*Generated on ).*?\*",
        lambda m: f"{m.group(1)}{datetime.now():%Y-%m-%d %H:%M:%S}*",
        content,
    )
    content = re.sub(
        r"(Script Validation[^0-9]*)([0-9,]+)",
        lambda m: f"{m.group(1)}{metrics['scripts']:,}",
        content,
    )
    content = re.sub(
        r"([0-9,]+\s*Synchronized Databases)",
        f"{metrics['databases']:,} Synchronized Databases",
        content,
    )
    content = re.sub(
        r"([0-9,]+\s*databases operational)",
        f"{metrics['databases']:,} databases operational",
        content,
    )
    path.write_text(content)


def main() -> None:
    metrics = get_metrics()
    for path in README_PATHS:
        if path.exists():
            update_file(path, metrics)


if __name__ == "__main__":
    main()
