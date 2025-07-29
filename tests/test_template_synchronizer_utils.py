import sqlite3
from pathlib import Path

from template_engine import template_synchronizer


def test_cluster_templates_basic() -> None:
    templates = {"a": "foo bar", "b": "foo baz", "c": "baz qux"}
    reps = template_synchronizer._cluster_templates(templates, n_clusters=2)
    assert set(reps).issubset(templates)
    assert 1 <= len(reps) <= len(templates)


def test_compliance_score(tmp_path: Path, monkeypatch) -> None:
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE compliance_rules (pattern TEXT)")
        conn.execute("INSERT INTO compliance_rules VALUES ('forbidden')")
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    score_bad = template_synchronizer._compliance_score("forbidden call")
    score_good = template_synchronizer._compliance_score("safe code")
    assert score_bad == 50.0
    assert score_good == 100.0
