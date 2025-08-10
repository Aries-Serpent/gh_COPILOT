import sqlite3

from scripts.quick_database_query import log_metrics


def test_log_metrics_creates_table_and_index(tmp_path):
    db = tmp_path / "analytics.db"
    log_metrics("success", db)

    with sqlite3.connect(db) as conn:
        cols = {row[1]: row for row in conn.execute("PRAGMA table_info(script_metrics)")}
        assert "id" in cols and cols["id"][5] == 1  # primary key
        assert "ts" in cols

        indexes = [row[1] for row in conn.execute("PRAGMA index_list(script_metrics)")]
        assert "idx_script_metrics_ts" in indexes

        cur = conn.execute("SELECT script, status, ts FROM script_metrics")
        row = cur.fetchone()
        assert row[0] == "quick_database_query"
        assert row[1] == "success"
        assert isinstance(row[2], int)

