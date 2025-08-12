from pathlib import Path
import sqlite3

from ghc_monitoring.baseline_anomaly_detector import BaselineAnomalyDetector


def _create_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE performance_metrics(system_health_score REAL)"
        )
        data = [(1.0,), (1.1,), (0.9,), (1.2,), (0.95,), (1.05,), (1.0,), (1.1,), (0.98,), (1.02,), (100.0,)]
        conn.executemany(
            "INSERT INTO performance_metrics(system_health_score) VALUES (?)",
            data,
        )
        conn.commit()


def test_detects_outlier(tmp_path: Path) -> None:
    db = tmp_path / "monitoring.db"
    _create_db(db)
    detector = BaselineAnomalyDetector(db_path=db, threshold=2.0)
    assert detector.detect()[-1]
