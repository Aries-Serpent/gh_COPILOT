import json
import sqlite3
import datetime
from datetime import timedelta

from complete_template_generator import CompleteTemplateGenerator
from unified_script_generation_system import EnterpriseUtility


def test_cluster_templates(tmp_path):
    t1 = tmp_path / "one.txt"
    t2 = tmp_path / "two.txt"
    t1.write_text("{a}{b}")
    t2.write_text("{a}")
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    clusters = util.cluster_templates([t1, t2], n_clusters=2)
    assert len(clusters) == 2
    cluster_file = tmp_path / "cluster_output.json"
    assert cluster_file.exists()
    data = json.loads(cluster_file.read_text())
    assert sum(len(v) for v in data.values()) == 2


def test_cleanup_legacy_assets(tmp_path):
    db = tmp_path / "prod.db"
    gen = CompleteTemplateGenerator(production_db=db)
    old = (datetime.datetime.now(datetime.timezone.utc) - timedelta(days=40)).isoformat()
    new = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO template_generation_stats (cluster_id, template_length, generated_at) VALUES (1, 10, ?)",
            (old,),
        )
        conn.execute(
            "INSERT INTO template_generation_stats (cluster_id, template_length, generated_at) VALUES (1, 10, ?)",
            (new,),
        )
        conn.execute(
            "INSERT INTO generated_templates (template_id, template_content, generated_at) VALUES ('old', 'x', ?)",
            (old,),
        )
        conn.execute(
            "INSERT INTO generated_templates (template_id, template_content, generated_at) VALUES ('new', 'y', ?)",
            (new,),
        )
        conn.commit()
    removed = gen.cleanup_legacy_assets(retention_days=30)
    with sqlite3.connect(db) as conn:
        stats = conn.execute("SELECT COUNT(*) FROM template_generation_stats").fetchone()[0]
        generated = conn.execute("SELECT COUNT(*) FROM generated_templates").fetchone()[0]
    assert removed == 2
    assert stats == 1
    assert generated == 1
