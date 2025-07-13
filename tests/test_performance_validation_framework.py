import sqlite3
import time
from pathlib import Path


from performance_validation_framework import PerformanceValidationFramework


def _patch_algorithms(monkeypatch, delay: float) -> None:
    def _sleep(*args, **kwargs):
        time.sleep(delay)
        return {}

    monkeypatch.setattr(
        'performance_validation_framework.run_grover_search', _sleep
    )
    monkeypatch.setattr(
        'performance_validation_framework.run_kmeans_clustering', _sleep
    )
    monkeypatch.setattr(
        'performance_validation_framework.run_simple_qnn', _sleep
    )
    monkeypatch.setattr(
        'performance_validation_framework.TemplateSynthesisEngine.synthesize_templates',
        lambda self: ["tmpl"] * 5
    )
    monkeypatch.setattr(
        'performance_validation_framework.Database \
            DrivenFlake8CorrectorFunctional.scan_python_files',
        lambda self: [Path("a.py")] * 5
    )
    monkeypatch.setattr(
        'performance_validation_framework.DatabaseD \
            rivenFlake8CorrectorFunctional.execute_correction',
        lambda self: True
    )
    monkeypatch.setattr(
        'performance_validation_framework.SecondaryCopilotValidator.validate_corrections',
        lambda self, files: True
    )


def test_baseline_and_regressions(tmp_path, monkeypatch):
    db = tmp_path / "prod.db"
    # initial slower run
    _patch_algorithms(monkeypatch, 0.02)
    framework = PerformanceValidationFramework(str(db))
    baseline = framework.run_benchmarks(store_baseline=True)
    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM performance_baseline"
        ).fetchone()[0]
    assert count == len(baseline)

    # faster second run
    _patch_algorithms(monkeypatch, 0.01)
    metrics = framework.run_benchmarks()
    diff = framework.compare_to_baseline(metrics)
    assert diff["grover_time"] < 0
    assert diff["template_throughput"] > 0
    assert diff["flake8_rate"] > 0
