import sqlite3
import threading
import time

from scripts.database import template_asset_ingestor as tai


def test_ingest_templates_respects_busy_timeout(tmp_path, monkeypatch):
    monkeypatch.setenv("BUSY_TIMEOUT_MS", "1000")
    workspace = tmp_path
    prompts = workspace / "prompts"
    prompts.mkdir()
    (prompts / "a.md").write_text("hi")

    db_path = workspace / "databases" / "enterprise_assets.db"
    tai._initialize_database(db_path)

    # Avoid extra initialization during the test
    monkeypatch.setattr(tai, "_initialize_database", lambda _: None)

    def hold_lock():
        conn = sqlite3.connect(db_path, timeout=0)
        conn.execute("BEGIN EXCLUSIVE")
        time.sleep(0.3)
        conn.commit()
        conn.close()

    t = threading.Thread(target=hold_lock)
    t.start()
    time.sleep(0.1)

    tai.ingest_templates(workspace, prompts)
    t.join()

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
    assert count == 1
