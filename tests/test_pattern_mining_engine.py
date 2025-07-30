import os
import sqlite3
from pathlib import Path

from template_engine.pattern_mining_engine import (
    extract_patterns,
    mine_patterns,
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

def test_mine_patterns(tmp_path: Path):
    # Start time logging for visual processing indicator
    from datetime import datetime
    start_time = datetime.now()
    print(f"PROCESS STARTED: test_mine_patterns")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (template_code) VALUES ('def x(): pass')"
        )
    analytics = tmp_path / "analytics.db"
    patterns = mine_patterns(prod, analytics)
    assert patterns, "No patterns mined from templates"
    with sqlite3.connect(prod) as conn:
        count = conn.execute("SELECT COUNT(*) FROM mined_patterns").fetchone()[0]
    assert count == len(patterns), "Pattern count mismatch in mined_patterns table"
    assert validate_mining(len(patterns), analytics), "DUAL COPILOT validation failed"


def test_mine_patterns_clusters(tmp_path: Path) -> None:
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
