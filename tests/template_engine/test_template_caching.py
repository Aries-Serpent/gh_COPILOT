import sqlite3
from pathlib import Path

from template_engine.auto_generator import TemplateAutoGenerator
from tests.template_engine.test_database_scoring import (
    create_test_dbs,
    create_production_db,
)


def test_rank_templates_caches_results(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    analytics_db, completion_db = create_test_dbs(tmp_path)
    prod = create_production_db(tmp_path, "foo")

    gen = TemplateAutoGenerator(analytics_db, completion_db, production_db=prod)

    first = gen.rank_templates("foo")
    second = gen.rank_templates("foo")
    assert first == second

    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM generator_events WHERE event='cache_hit'"
        ).fetchone()[0]
    assert count == 1
