#!/usr/bin/env python3
import logging
import sqlite3

from scripts.optimization.advanced_qubo_optimization import (
    solve_qubo_bruteforce,
)


class SimpleDummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(self, iterable, *args, **kwargs):
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

logging.getLogger().setLevel(logging.CRITICAL)


def test_solve_qubo_bruteforce(monkeypatch):
    matrix = [[1.0, -2.0], [-2.0, 1.0]]
    bars = []

    def dummy_tqdm(iterable, *args, **kwargs):
        bar = RecordingDummyTqdm(iterable)
        bars.append(bar)
        return bar

    monkeypatch.setattr(
        "scripts.optimization.advanced_qubo_optimization.tqdm", dummy_tqdm
    )

    solution, energy = solve_qubo_bruteforce(matrix)

    assert solution == [1, 1]
    assert energy == -2.0


class RecordingDummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(self, iterable, *args, **kwargs):
        self.iterable = list(iterable)
        self.total = len(self.iterable)
        self.updates = 0

    def __iter__(self):
        for item in self.iterable:
            yield item
            self.updates += 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_execute_utility_progress_and_db(tmp_path, monkeypatch, caplog):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "production.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, category TEXT, name TEXT)")
        conn.execute("INSERT INTO code_templates (category, name) VALUES ('optimization', 'opt')")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    bars = []

    def dummy_tqdm(iterable, *args, **kwargs):
        bar = RecordingDummyTqdm(iterable, *args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr("scripts.optimization.advanced_qubo_optimization.tqdm", dummy_tqdm)

    called = {"valid": False}

    class DummyValidator:
        def __init__(self, logger=None) -> None:
            pass

        def validate_corrections(self, files):
            called["valid"] = True
            return True

    monkeypatch.setattr(
        "scripts.optimization.advanced_qubo_optimization.SecondaryCopilotValidator",
        lambda logger=None: DummyValidator(),
    )

    with caplog.at_level(logging.INFO):
        from scripts.optimization import advanced_qubo_optimization as aqo

        assert aqo.main() is True

    assert bars and bars[0].updates == 4
    assert "Loaded 1 optimization templates" in caplog.text
    assert called["valid"]
