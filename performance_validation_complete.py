#!/usr/bin/env python3
"""PerformanceValidationComplete
===============================

Benchmark quantum algorithms, template synthesis speed, and flake8
correction throughput. Results are logged for operational monitoring.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from tqdm import tqdm

from database_driven_flake8_corrector_functional import \
    DatabaseDrivenFlake8CorrectorFunctional
from quantum_algorithms_functional import (run_grover_search,
                                           run_kmeans_clustering,
                                           run_simple_qnn)
from template_auto_generation_complete import TemplateSynthesisEngine

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "progress": "[PROGRESS]",
}

logger = logging.getLogger(__name__)

DB_PATH = Path("benchmark_metrics.db")


def _init_db(db_path: Path) -> sqlite3.Connection:
    """Return SQLite connection and ensure table exists."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            grover_time REAL,
            kmeans_time REAL,
            qnn_time REAL,
            template_time REAL,
            flake8_time REAL
        )
        """
    )
    return conn


def _get_last_metrics(conn: sqlite3.Connection) -> Optional[Dict[str, float]]:
    """Return the most recent metrics row if available."""
    cursor = conn.execute(
        "SELECT grover_time, kmeans_time, qnn_time, template_time, flake8_time"
        " FROM performance_metrics ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "grover_time": row[0],
        "kmeans_time": row[1],
        "qnn_time": row[2],
        "template_time": row[3],
        "flake8_time": row[4],
    }


def benchmark(db_path: Path | str = DB_PATH) -> Dict[str, float]:
    """Run benchmarks and return timing metrics.

    The function stores results in ``performance_metrics`` SQLite table and
    compares them to the last stored run. Any slower metric triggers a
    warning log entry.
    """
    metrics: Dict[str, float] = {}
    db_path = Path(db_path)
    conn = _init_db(db_path)
    baseline = _get_last_metrics(conn)

    with tqdm(total=3, desc=f"{TEXT_INDICATORS['progress']} benchmark") as bar:
        start = time.perf_counter()
        run_grover_search([1, 2, 3, 4], 3)
        metrics["grover_time"] = time.perf_counter() - start
        bar.update(1)

        start = time.perf_counter()
        run_kmeans_clustering(samples=100, clusters=2)
        metrics["kmeans_time"] = time.perf_counter() - start
        bar.update(1)

        start = time.perf_counter()
        run_simple_qnn()
        metrics["qnn_time"] = time.perf_counter() - start
        bar.update(1)

    start = time.perf_counter()
    engine = TemplateSynthesisEngine()
    engine.synthesize_templates()
    metrics["template_time"] = time.perf_counter() - start

    tmp_dir = Path(".tmp_flake8")
    tmp_dir.mkdir(exist_ok=True)
    test_file = tmp_dir / "bad.py"
    test_file.write_text("print('hi')  \n")
    start = time.perf_counter()
    corrector = DatabaseDrivenFlake8CorrectorFunctional(workspace_path=str(tmp_dir))
    corrector.execute_correction()
    metrics["flake8_time"] = time.perf_counter() - start

    if baseline:
        for key, value in metrics.items():
            baseline_value = baseline.get(key)
            if baseline_value is not None and value > baseline_value:
                logger.warning(
                    "%s regressed from %.3fs to %.3fs",
                    key,
                    baseline_value,
                    value,
                )

    conn.execute(
        """
        INSERT INTO performance_metrics (
            timestamp, grover_time, kmeans_time, qnn_time, template_time, flake8_time
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(),
            metrics["grover_time"],
            metrics["kmeans_time"],
            metrics["qnn_time"],
            metrics["template_time"],
            metrics["flake8_time"],
        ),
    )
    conn.commit()
    conn.close()

    return metrics


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    results = benchmark()
    for k, v in results.items():
        print(f"{k}: {v:.3f}s")
