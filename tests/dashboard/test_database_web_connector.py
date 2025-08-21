from __future__ import annotations

import sqlite3
from pathlib import Path

from web_gui.scripts.flask_apps.database_web_connector import DatabaseWebConnector


def _create_temp_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE enterprise_metrics(metric_name TEXT, metric_value REAL, metric_unit TEXT)"
    )
    cur.execute(
        "INSERT INTO enterprise_metrics VALUES('compliance_score', 95.5, 'percent')"
    )

    cur.execute(
        """
        CREATE TABLE system_monitoring_live(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            enterprise_readiness REAL,
            anomalies_detected TEXT,
            metrics_json TEXT
        )
        """
    )
    cur.execute(
        """
        INSERT INTO system_monitoring_live(
            timestamp,
            cpu_usage,
            memory_usage,
            disk_usage,
            enterprise_readiness,
            anomalies_detected,
            metrics_json
        )
        VALUES(datetime('now'),50.0,60.0,70.0,0.9,'none','{"extra":1}')
        """
    )

    cur.execute(
        """
        CREATE TABLE performance_metrics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            operation_type TEXT,
            execution_time REAL,
            files_processed INTEGER,
            success_rate REAL,
            memory_usage REAL,
            system_resources TEXT
        )
        """
    )
    cur.execute(
        """
        INSERT INTO performance_metrics(
            operation_type,
            execution_time,
            files_processed,
            success_rate,
            memory_usage,
            system_resources
        )
        VALUES('sync',1.5,10,0.99,100.0,'{"cpu":50}')
        """
    )
    conn.commit()
    conn.close()


def test_connection_pool_reuses_connection(tmp_path) -> None:
    db_file = tmp_path / "test.db"
    _create_temp_db(db_file)
    connector = DatabaseWebConnector(db_file, pool_size=1)
    with connector.get_database_connection() as conn1:
        pass
    with connector.get_database_connection() as conn2:
        pass
    assert conn1 is conn2
    assert connector._pool.qsize() == 1
    connector.close_pool()


def test_fetch_latest_metrics(tmp_path) -> None:
    db_file = tmp_path / "test.db"
    _create_temp_db(db_file)
    connector = DatabaseWebConnector(db_file)

    sys_metrics = connector.fetch_latest_system_metrics()
    assert sys_metrics["cpu_usage"] == 50.0
    assert sys_metrics["metrics_json"]["extra"] == 1

    perf_metrics = connector.fetch_latest_performance_metrics()
    assert perf_metrics["operation_type"] == "sync"
    assert perf_metrics["system_resources"]["cpu"] == 50

    enterprise_metrics = connector.fetch_enterprise_metrics()
    assert enterprise_metrics["compliance_score"]["value"] == 95.5
    assert enterprise_metrics["compliance_score"]["unit"] == "percent"
    connector.close_pool()
