import os
import sqlite3
from pathlib import Path
import types
import pytest

import template_engine.pattern_mining_engine as pme
from template_engine.pattern_mining_engine import (
    extract_patterns,
    mine_patterns,
    get_clusters,
    validate_mining,
)


def test_extract_patterns():
    # Start time logging for visual processing indicator
    from datetime import datetime

    start_time = datetime.now()
    print(f"PROCESS STARTED: test_extract_patterns")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    templates = ["def foo(bar): return bar", "def foo(baz): return baz"]
    patterns = extract_patterns(templates)
    assert any("def foo" in p for p in patterns)

    # Completion summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"TEST COMPLETED: test_extract_patterns in {duration:.2f}s")


def test_mine_patterns(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(pme, "_log_audit_real", lambda *a, **k: None)
    # Start time logging for visual processing indicator
    from datetime import datetime

    start_time = datetime.now()
    print(f"PROCESS STARTED: test_mine_patterns")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
    analytics = tmp_path / "analytics.db"
    patterns = mine_patterns(prod, analytics)
    assert patterns, "No patterns mined from templates"
    with sqlite3.connect(prod) as conn:
        count = conn.execute("SELECT COUNT(*) FROM mined_patterns").fetchone()[0]
    assert count == len(patterns), "Pattern count mismatch in mined_patterns table"
    assert validate_mining(len(patterns), analytics), "DUAL COPILOT validation failed"


def test_mine_patterns_clusters(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(pme, "_log_audit_real", lambda *a, **k: None)
    from datetime import datetime

    start_time = datetime.now()
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def y(): pass')")
    mine_patterns(prod, analytics)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM pattern_clusters").fetchone()[0]
    assert count > 0

    # Completion summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"TEST COMPLETED: test_mine_patterns in {duration:.2f}s")


def test_get_clusters_and_audit_logging(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def y(): pass')")

    def audit_log(db_name: str, details: str) -> None:
        with sqlite3.connect(analytics) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, db_name TEXT, details TEXT, ts TEXT)"
            )
            conn.execute(
                "INSERT INTO audit_log (db_name, details, ts) VALUES (?, ?, ?)",
                (db_name, details, "test"),
            )
            conn.commit()

    monkeypatch.setattr(pme, "_log_audit_real", audit_log)
    mine_patterns(prod, analytics)
    clusters = get_clusters(analytics)
    assert clusters
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    assert count > 0


def test_mine_patterns_timeout_storage(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(pme, "_log_audit_real", lambda *a, **k: None)

    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
    analytics = tmp_path / "analytics.db"

    t = types.SimpleNamespace(count=-1)

    def fake_time() -> int:
        t.count += 1
        return t.count

    monkeypatch.setattr(pme.time, "time", fake_time)
    with pytest.raises(TimeoutError):
        mine_patterns(prod, analytics, timeout_minutes=0)


def test_mine_patterns_timeout_clustering(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(pme, "_log_audit_real", lambda *a, **k: None)

    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def y(): pass')")
    analytics = tmp_path / "analytics.db"

    monkeypatch.setattr(pme.time, "time", lambda: 0)

    orig_fit = pme.KMeans.fit_predict

    def fake_fit(self, vec):
        monkeypatch.setattr(pme.time, "time", lambda: 1000)
        return orig_fit(self, vec)

    monkeypatch.setattr(pme.KMeans, "fit_predict", fake_fit)

    with pytest.raises(TimeoutError):
        mine_patterns(prod, analytics, timeout_minutes=1)
