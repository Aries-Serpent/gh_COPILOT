import sqlite3
from pathlib import Path

from template_engine import pattern_mining_engine as pme


def test_cross_reference_aggregation(tmp_path: Path) -> None:
    analytics = tmp_path / "analytics.db"
    analytics.parent.mkdir(exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE cross_link_events (file_path TEXT, linked_path TEXT)")
        conn.executemany(
            "INSERT INTO cross_link_events VALUES (?, ?)",
            [("a.py", "b.py"), ("a.py", "c.py"), ("b.py", "d.py")],
        )
    counts = pme.aggregate_cross_references(analytics_db=analytics)
    assert counts.get("a.py") == 2
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT file_path, links FROM cross_reference_aggregate").fetchall()
    assert ("a.py", 2) in rows
