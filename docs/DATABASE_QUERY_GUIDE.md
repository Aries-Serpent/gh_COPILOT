# Database Query Guide

This guide demonstrates how to query the primary databases before creating new code or documentation.

## 1. production.db

Use this database to retrieve existing scripts and templates.

```python
import sqlite3
from pathlib import Path

workspace = Path(os.environ.get("GH_COPILOT_WORKSPACE", "."))
with sqlite3.connect(workspace / "databases" / "production.db") as conn:
    row = conn.execute(
        "SELECT script_path FROM script_repository WHERE script_type='utility' LIMIT 1"
    ).fetchone()
    script = Path(row[0]).read_text()
    print(script)
```

## 2. template_documentation.db

Patterns for template synthesis reside here.

```python
with sqlite3.connect(workspace / "archives" / "template_documentation.db") as conn:
    for tid, content in conn.execute("SELECT template_id, content FROM template_metadata LIMIT 3"):
        print(tid, content[:40])
```

## 3. documentation.db

Documentation templates are stored in this database. The `documentation_generation_system.py` script reads from it and writes Markdown files under `documentation/generated/templates`.

```python
with sqlite3.connect(workspace / "databases" / "documentation.db") as conn:
    templates = conn.execute(
        "SELECT template_name FROM documentation_templates WHERE enterprise_compliant=1"
    ).fetchall()
    for (name,) in templates:
        print(name)
```

### Cross References

- `scripts/documentation_generation_system.py`
- `scripts/documentation_consolidator.py`
- `scripts/documentation/enterprise_documentation_manager.py`
- `scripts/utilities/complete_template_generator.py`

These utilities rely on the databases above to generate scripts and docs.
