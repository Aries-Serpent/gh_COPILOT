"""Template database synchronization utilities."""
from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from pathlib import Path
from typing import Iterable

ANALYTICS_DB = Path(os.getenv("ANALYTICS_DB", "analytics.db"))

logger = logging.getLogger(__name__)


def _log_event(db_path: Path, success: bool, error: str | None = None) -> None:
    ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        if success:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS sync_events(db TEXT)"
            )
            conn.execute(
                "INSERT INTO sync_events(db) VALUES (?)",
                (str(db_path),),
            )
            conn.commit()
        if error:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS audit_log(db TEXT, error TEXT)"
            )
            conn.execute(
                "INSERT INTO audit_log(db, error) VALUES (?, ?)", (str(db_path), error)
            )
            conn.commit()


def _load_templates(conn: sqlite3.Connection) -> dict[str, str]:
    has_table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='templates'"
    ).fetchone()
    if not has_table:
        raise sqlite3.OperationalError("missing templates table")
    rows = conn.execute(
        "SELECT name, template_content FROM templates"
    ).fetchall()
    return {name: content for name, content in rows if content}


def synchronize_templates_real(databases: Iterable[Path]) -> None:
    """Synchronize templates across ``databases`` transactionally."""
    templates: dict[str, str] = {}
    valid_dbs: list[Path] = []
    # gather templates
    for db in databases:
        with sqlite3.connect(db) as conn:
            try:
                templates.update(_load_templates(conn))
                valid_dbs.append(db)
            except sqlite3.Error as exc:  # pragma: no cover - should not happen in tests
                logger.exception("Failed reading templates from %s", db)
                _log_event(db, False, str(exc))
                continue
    # apply templates only to valid databases
    for db in valid_dbs:
        with sqlite3.connect(db) as conn:
            try:
                conn.execute("BEGIN")
                _load_templates(conn)  # validate presence of table
                conn.executemany(
                    "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                    list(templates.items()),
                )
                conn.commit()
                _log_event(db, True)
            except sqlite3.Error as exc:
                conn.rollback()
                logger.exception("Synchronization failed for %s", db)
                _log_event(db, False, str(exc))


def synchronize_templates(databases: Iterable[Path], *, real: bool = True) -> None:
    if real:
        synchronize_templates_real(databases)
    else:
        for db in databases:
            logger.info("[SIMULATION] Would synchronize templates for %s", db)
            _log_event(db, True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Template Synchronizer")
    parser.add_argument("databases", nargs="+", type=Path)
    parser.add_argument("--real", action="store_true", help="Run in real mode")
    args = parser.parse_args(argv)

    synchronize_templates(args.databases, real=args.real)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
