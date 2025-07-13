#!/usr/bin/env python3
"""Validate documentation metrics against production database."""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "production.db"
README_PATH = ROOT / "README.md"
GENERATED_README = ROOT / "documentation" / "generated" / "README.md"
WHITEPAPER_PATH = ROOT / "COMPLETE_TECHNICAL_SPECIFICATIONS_WHITEPAPER.md"
DATABASE_LIST = ROOT / "documentation" / "DATABASE_LIST.md"


def get_db_metrics(db_path: Path) -> dict[str, int]:
    """Return metrics from the production database."""
    conn = sqlite3.connect(db_path)
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


def parse_readme(path: Path) -> dict[str, int]:
    """Parse metrics from a README file."""
    metrics: dict[str, int] = {}
    regex = re.compile(r"(\d[\d,]*)")
    with path.open() as f:
        for line in f:
            if "Script Validation" in line and "scripts" in line:
                m = regex.search(line)
                if m:
                    metrics["scripts"] = int(m.group(1).replace(",", ""))
            elif "Synchronized Databases" in line:
                m = regex.search(line)
                if m:
                    metrics["databases"] = int(m.group(1).replace(",", ""))
    return metrics


def parse_template_metric(path: Path) -> int | None:
    """Return template count referenced in the whitepaper if present."""
    regex = re.compile(r"(\d+)\s+Templates")
    with path.open() as f:
        for line in f:
            m = regex.search(line)
            if m:
                return int(m.group(1))
    return None


def validate() -> bool:
    """Validate metrics across documentation."""
    db_metrics = get_db_metrics(DB_PATH)
    readme_metrics = parse_readme(README_PATH)
    generated_metrics = parse_readme(GENERATED_README)
    whitepaper_templates = parse_template_metric(WHITEPAPER_PATH)

    success = True

    for key in ("scripts", "databases"):
        expected = db_metrics.get(key)
        for metrics_source, metrics in [
            ("README", readme_metrics),
            ("generated/README", generated_metrics),
        ]:
            actual = metrics.get(key)
            if actual != expected:
                print(
                    f"Mismatch in {metrics_source} for {key}: {actual} vs {expected}",
                    file=sys.stderr,
                )
                success = False

    if whitepaper_templates is not None and whitepaper_templates != db_metrics["templates"]:
        print(
            f"Mismatch in whitepaper templates: {whitepaper_templates} vs {
    db_metrics['templates']}",
            file=sys.stderr,
        )
        success = False

    if success:
        print("All documentation metrics are consistent.")
    return success


if __name__ == "__main__":
    sys.exit(0 if validate() else 1)
