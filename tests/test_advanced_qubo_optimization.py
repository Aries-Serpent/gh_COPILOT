import logging
import sqlite3
from typing import Any

from scripts.optimization.advanced_qubo_optimization import EnterpriseUtility


class DummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(self, iterable, *args: Any, **kwargs: Any) -> None:
        self.iterable = list(iterable)
        self.updates = 0

    def __iter__(self):
        for item in self.iterable:
            self.updates += 1
            yield item

    def set_postfix(self, data):
        pass

    def close(self):
        pass


class DummyValidator:
    def __init__(self, logger=None) -> None:
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


def test_execute_utility_queries_db(monkeypatch, tmp_path, caplog):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE template_repository (template_name TEXT, template_category TEXT, template_content TEXT)"
        )
        conn.execute(
            "INSERT INTO template_repository VALUES ('temp', 'optimization', 'pass')"
        )

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    bars = []

    def dummy_tqdm(iterable, *args: Any, **kwargs: Any) -> DummyTqdm:
        bar = DummyTqdm(iterable)
        bars.append(bar)
        return bar

    monkeypatch.setattr(
        "scripts.optimization.advanced_qubo_optimization.tqdm", dummy_tqdm
    )

    dummy = DummyValidator()
    monkeypatch.setattr(
        "scripts.optimization.advanced_qubo_optimization.SecondaryCopilotValidator",
        lambda logger=None: dummy,
    )

    util = EnterpriseUtility()
    with caplog.at_level(logging.INFO):
        assert util.execute_utility() is True

    assert bars and bars[0].updates == 4
    assert dummy.called
    assert any(
        "Loaded 1 optimization templates" in rec.getMessage() for rec in caplog.records
    )
