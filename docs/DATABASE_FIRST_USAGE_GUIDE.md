# Database-First Usage Guide

This guide describes how to operate the **gh_COPILOT** toolkit using the recommended database-first workflow.

Set the ``GH_COPILOT_WORKSPACE`` environment variable to the repository root so
utility scripts locate databases and output paths correctly. Example:

```bash
export GH_COPILOT_WORKSPACE=/path/to/gh_COPILOT
```

## 1. Query Before Code
- Always query `production.db`, `template_documentation.db` or `documentation.db` for existing patterns before creating new code or documentation.
- Example:
  ```python
  import sqlite3
  with sqlite3.connect('databases/production.db') as conn:
      cur = conn.cursor()
      cur.execute("SELECT content FROM code_templates WHERE name=?", ('build_script',))
      template = cur.fetchone()[0]
  ```

## 2. Generate From Templates
- Use retrieved templates as the base for new scripts.
- Log template usage in `template_usage_tracking` for auditing.
- Templates may include placeholders such as `{workspace}` which will be
  automatically replaced with the active workspace path by
  `DatabaseFirstCopilotEnhancer`.
- To automatically cluster templates and extract representative examples, use
  `template_engine.auto_generator.TemplateAutoGenerator`. It relies on
  `sklearn.cluster.KMeans` and provides a `get_cluster_representatives()` method
  for retrieving key patterns.

## 3. Documentation Generation
- Documentation patterns are stored in `documentation.db`.
- Render Markdown files from these entries and record the generation event.

## 4. Synchronization
- Run `synchronize_templates()` to ensure templates are consistent across all databases.

## 5. Compliance & Correction
- All generation actions must be logged for compliance review.
- When corrections occur, update `analytics.db:correction_patterns` for future reference.

