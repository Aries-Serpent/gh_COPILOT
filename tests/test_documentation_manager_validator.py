import os
import sqlite3
from pathlib import Path

from archive.consolidated_scripts.enterprise_database_driven_documentation_manager import (
    DocumentationManager,
    dual_validate,
)
from template_engine import auto_generator

auto_generator.validate_no_recursive_folders = lambda: None


def test_documentation_validator(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir(parents=True)
    completion_db = tmp_path / "template.db"

    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE documentation (title TEXT, content TEXT, compliance_score INTEGER)")
        conn.execute("INSERT INTO documentation VALUES ('Doc1', 'body', 80)")

    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('{content}')")

    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (replacement_template TEXT)")
        conn.execute("INSERT INTO ml_pattern_optimization VALUES ('{content}')")

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    manager = DocumentationManager(
        database=prod_db,
        analytics_db=analytics,
        completion_db=completion_db,
    )
    assert manager.render() == 1
    import archive.consolidated_scripts.enterprise_database_driven_documentation_manager as mod

    mod_obj = manager
    setattr(mod, "DocumentationManager", lambda: mod_obj)
    assert dual_validate()
