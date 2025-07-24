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
- Use `scripts/documentation/enterprise_documentation_manager.py` to render Markdown files from these entries and record the generation event.
- Rendered output is also saved to `logs/template_rendering/` with timestamped filenames for auditing.

## 4. Synchronization
- Run `template_engine.template_synchronizer.synchronize_templates()` to ensure
  templates are consistent across development, staging, and production
  databases.

## 5. Compliance & Correction
- All generation actions must be logged for compliance review.
- When corrections occur, update `analytics.db:correction_patterns` for future reference.
- Placeholder detection results are written to `analytics.db:placeholder_audit` and mirrored in `code_audit_log` for dashboard reporting.
- Script generation events are recorded in `production.db:enhanced_script_tracking` with the
  template version and a computed compliance score.
- The `EnterpriseComplianceValidator` verifies that every generated script comes from an approved
  template and meets the minimum compliance threshold (usually 80%).
- Compliance summaries are exported to `analytics.db` so auditors can trace which templates were
   used and whether any corrective actions occurred.

The Flask dashboard exposes a `/dashboard/compliance` endpoint that reads these
metrics and shows real-time placeholder removal progress.

## 6. Database Maintenance

Regularly monitor the size of each SQLite database under `databases/`. Databases
should remain below **99.9 MB** to maintain optimal performance. The
`scripts/automation/autonomous_database_health_optimizer.py` module can be used
to check sizes and integrity metrics. When a database grows too large,
purification or archival scripts (for example,
`scripts/database/database_purification_engine.py`) should be run to compress
tables and move historical records to the `archives/` directory. This periodic
cleanup keeps active databases lean while preserving old data for future
reference.

