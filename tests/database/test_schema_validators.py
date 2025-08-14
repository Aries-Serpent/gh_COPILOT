from pathlib import Path
import re
import sqlite3

import pytest

from scripts.database.schema_validators import (
    ensure_documentation_schema,
    ensure_har_schema,
    ensure_template_schema,
)
from scripts.database.unified_database_initializer import TABLES


def _create_db(tmp_path: Path, table: str, omit: str | None = None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    db = tmp_path / "db.sqlite"
    stmt = TABLES[table]
    if omit:
        stmt = re.sub(rf"{omit}[^,]*,?", "", stmt)
    with sqlite3.connect(db) as conn:
        conn.execute(stmt)
        conn.commit()
    return db


def test_ensure_documentation_schema_pass(tmp_path: Path) -> None:
    db = _create_db(tmp_path, "documentation_assets")
    ensure_documentation_schema(db)


def test_ensure_documentation_schema_missing(tmp_path: Path) -> None:
    db = _create_db(tmp_path, "documentation_assets", omit="version")
    with pytest.raises(RuntimeError):
        ensure_documentation_schema(db)


def test_template_and_har_validators(tmp_path: Path) -> None:
    tdb = _create_db(tmp_path / "t", "template_assets")
    hdb = _create_db(tmp_path / "h", "har_entries")
    ensure_template_schema(tdb)
    ensure_har_schema(hdb)

