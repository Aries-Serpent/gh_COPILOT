from pathlib import Path
import sqlite3

from src.monitoring.anomaly import AnomalyPipeline


def _write_history(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE sync_metrics (metric TEXT, value REAL)")
        rows = [("cpu", 1.0), ("cpu", 1.1), ("mem", 1.0), ("mem", 1.1)]
        conn.executemany("INSERT INTO sync_metrics (metric, value) VALUES (?, ?)", rows)
        conn.commit()


def test_pipeline_trains_and_detects(tmp_path: Path) -> None:
    db_path = tmp_path / "metrics.db"
    model_path = tmp_path / "model.pkl"
    _write_history(db_path)

    pipeline = AnomalyPipeline(model_path)
    pipeline.train(db_path)
    assert model_path.exists()

    # Create fresh instance to ensure loading from artifact works
    pipeline2 = AnomalyPipeline(model_path)
    result = pipeline2.evaluate({"cpu": 10.0, "mem": 1.0})
    assert result["cpu"]
    assert not result["mem"]
