import logging
import sqlite3
import time
from pathlib import Path

import pytest

from performance_validation_complete import benchmark


def test_benchmark_runs():
    results = benchmark()
    assert set(results.keys()) >= {"grover_time", "kmeans_time",
                                   "qnn_time", "template_time", "flake8_time"}
    for value in results.values():
        assert value >= 0


def test_metrics_are_stored(tmp_path, monkeypatch):
    db_file = tmp_path / "bench.db"

    monkeypatch.setattr(
        "performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_simple_qnn",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.TemplateSynthesisEngine.synthesize_templates",
        lambda self: None,
    )
    monkeypatch.setattr(
        "performance_validation_complete.DatabaseDrivenFlake8CorrectorFunctional.execute_correction",
        lambda self: True,
    )

    benchmark(db_path=db_file)
    with sqlite3.connect(db_file) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM performance_metrics"
        ).fetchone()[0]
    assert count == 1


def test_regression_warning(tmp_path, monkeypatch, caplog):
    db_file = tmp_path / "bench.db"

    # baseline run
    monkeypatch.setattr(
        "performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_simple_qnn",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "performance_validation_complete.TemplateSynthesisEngine.synthesize_templates",
        lambda self: None,
    )
    monkeypatch.setattr(
        "performance_validation_complete.DatabaseDrivenFlake8CorrectorFunctional.execute_correction",
        lambda self: True,
    )

    benchmark(db_path=db_file)

    # slower second run to trigger regression
    monkeypatch.setattr(
        "performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_simple_qnn",
        lambda *a, **k: time.sleep(0.02),
    )

    with caplog.at_level(logging.WARNING):
        benchmark(db_path=db_file)

    assert any("regressed" in rec.message for rec in caplog.records)
