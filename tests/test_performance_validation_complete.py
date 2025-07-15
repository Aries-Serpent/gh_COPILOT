#!/usr/bin/env python3
import logging
import sqlite3
import time


<<<<<<< HEAD
from scripts.validation.performance_validation_complete import benchmark
=======
from performance_validation_complete import benchmark
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_benchmark_runs():
    results = benchmark()
<<<<<<< HEAD
    assert set(results.keys()) >= {"grover_time", "kmeans_time", "qnn_time", "template_time", "flake8_time"}
=======
    assert set(results.keys()) >= {"grover_time", "kmeans_time",
                                   "qnn_time", "template_time", "flake8_time"}
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    for value in results.values():
        assert value >= 0


def test_metrics_are_stored(tmp_path, monkeypatch):
    db_file = tmp_path / "bench.db"

    monkeypatch.setattr(
<<<<<<< HEAD
        "scripts.validation.performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_simple_qnn",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.TemplateSynthesisEngine.synthesize_templates",
        lambda self: None,
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.DatabaseD \
=======
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
        "performance_validation_complete.DatabaseD \
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
            rivenFlake8CorrectorFunctional.execute_correction",
        lambda self: True,
    )

    benchmark(db_path=db_file)
    with sqlite3.connect(db_file) as conn:
<<<<<<< HEAD
        count = conn.execute("SELECT COUNT(*) FROM performance_metrics").fetchone()[0]
=======
        count = conn.execute(
            "SELECT COUNT(*) FROM performance_metrics"
        ).fetchone()[0]
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    assert count == 1


def test_regression_warning(tmp_path, monkeypatch, caplog):
    db_file = tmp_path / "bench.db"

    # baseline run
    monkeypatch.setattr(
<<<<<<< HEAD
        "scripts.validation.performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_simple_qnn",
        lambda *a, **k: time.sleep(0.01),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.TemplateSynthesisEngine.synthesize_templates",
        lambda self: None,
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.DatabaseD \
=======
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
        "performance_validation_complete.DatabaseD \
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
            rivenFlake8CorrectorFunctional.execute_correction",
        lambda self: True,
    )

    benchmark(db_path=db_file)

    # slower second run to trigger regression
    monkeypatch.setattr(
<<<<<<< HEAD
        "scripts.validation.performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "scripts.validation.performance_validation_complete.run_simple_qnn",
=======
        "performance_validation_complete.run_grover_search",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_kmeans_clustering",
        lambda *a, **k: time.sleep(0.02),
    )
    monkeypatch.setattr(
        "performance_validation_complete.run_simple_qnn",
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
        lambda *a, **k: time.sleep(0.02),
    )

    with caplog.at_level(logging.WARNING):
        benchmark(db_path=db_file)

    assert any("regressed" in rec.message for rec in caplog.records)
