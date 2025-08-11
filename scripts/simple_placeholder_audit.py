"""
Simple placeholder audit script.

Scans files for common placeholder tokens such as ``TODO`` or ``FIXME`` and
logs the findings to ``analytics.db``. Placeholder names defined in the
``production.db`` ``template_placeholders`` table are also detected.

For every file scanned a secondary copilot step runs ``flake8`` to validate
the file, following the dual‑copilot pattern.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List
from types import SimpleNamespace

from tqdm import tqdm

from enterprise_modules.compliance import enforce_anti_recursion
from scripts.database.add_code_audit_log import ensure_code_audit_log
from secondary_copilot_validator import SecondaryCopilotValidator
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

DEFAULT_TOKENS = ["TODO", "FIXME", "pass"]

_RECURSION_CTX = SimpleNamespace()


def load_canonical_tokens(db_path: Path) -> List[str]:
    """Return placeholder tokens defined in ``production.db``."""
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        try:
            cur = conn.execute("SELECT placeholder_name FROM template_placeholders")
            return [row[0] for row in cur.fetchall()]
        except sqlite3.Error:
            return []


def log_placeholder_event(db_path: Path, file_path: Path, line_number: int, token: str, context: str) -> None:
    """Insert a placeholder finding into ``analytics.db``."""
    ensure_code_audit_log(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO code_audit_log(file_path, line_number, "
            "placeholder_type, context, timestamp) VALUES (?, ?, ?, ?, ?)",
            (
                str(file_path),
                line_number,
                token,
                context,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def scan_file_for_placeholders(file_path: Path, tokens: Iterable[str]) -> List[tuple[int, str, str]]:
    """Return list of (line_number, token, context) for placeholders."""
    findings: List[tuple[int, str, str]] = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for i, line in enumerate(handle, 1):
            for token in tokens:
                if token in line:
                    findings.append((i, token, line.strip()))
    return findings


def audit_path(path: Path, analytics_db: Path, production_db: Path) -> int:
    """Scan ``path`` recursively and log all placeholder findings."""
    enforce_anti_recursion(_RECURSION_CTX)
    tokens = DEFAULT_TOKENS + load_canonical_tokens(production_db)
    files = [f for f in path.rglob("*") if f.is_file()]
    total = 0
    validator = SecondaryCopilotValidator()
    with tqdm(total=len(files), desc="placeholder-audit", unit="file") as bar:
        for file in files:
            findings = scan_file_for_placeholders(file, tokens)
            for line_number, token, context in findings:
                log_placeholder_event(analytics_db, file, line_number, token, context)
            if findings:
                validator.validate_corrections([str(file)])
            total += len(findings)
            bar.update(1)
    if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
        _RECURSION_CTX.recursion_depth -= 1
        ancestors = getattr(_RECURSION_CTX, "ancestors", [])
        if ancestors:
            ancestors.pop()
    return total


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan files for placeholders")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument(
        "--analytics-db",
        type=Path,
        default=Path("databases/analytics.db"),
        help="Path to analytics.db",
    )
    parser.add_argument(
        "--production-db",
        type=Path,
        default=Path("databases/production.db"),
        help="Path to production.db",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    path = args.path
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if path.is_file():
        total = audit_path(path.parent, args.analytics_db, args.production_db)
    else:
        total = audit_path(path, args.analytics_db, args.production_db)
    orchestrator = DualCopilotOrchestrator()
    orchestrator.validator.validate_corrections([str(path)])
    print(f"Logged {total} placeholder entries")
    return 0


if __name__ == "__main__":  # pragma: no cover - simple CLI
    raise SystemExit(main())
