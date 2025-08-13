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
- For production systems use
  `archive/consolidated_scripts/enterprise_database_driven_documentation_manager.py`.
  This manager now loads templates from both `documentation.db` and
  `production.db`, writing Markdown, HTML and JSON files for each compliant
  entry. Generation events are logged to `analytics.db:render_events` and
  progress metrics are written to `dashboard/compliance/metrics.json`.

## 4. Synchronization
- Run `template_engine.template_synchronizer.synchronize_templates()` to preview
   synchronization across development, staging, and production databases. To
  apply updates and record audit logs, use
  `template_engine.template_synchronizer.synchronize_templates_real()` or run
  the CLI with the `--real` flag. Pass `--cluster` to enable KMeans-based
  template grouping during synchronization.

## 5. Compliance & Correction
- All generation actions must be logged for compliance review.
- When corrections occur, update `analytics.db:correction_patterns` for future reference.
- Placeholder detection results are written to `analytics.db:placeholder_audit`  and mirrored in `code_audit_log` for dashboard reporting.
- Resolution tracking is enabled via `todo_fixme_tracking.status` and `resolved_timestamp` fields. Each removal links via `removal_id`. The table structure is:

| column | type |
| ------ | ---- |
| file_path | TEXT |
| line_number | INTEGER |
| placeholder_type | TEXT |
| context | TEXT |
| timestamp | DATETIME |
| resolved | BOOLEAN |
| resolved_timestamp | DATETIME |
| status | TEXT |
| removal_id | INTEGER |
- Run `python scripts/database/add_code_audit_log.py` or apply
  `databases/migrations/add_code_audit_log.sql` to ensure this table exists on
  older analytics databases.
- Script generation events are recorded in `production.db:enhanced_script_tracking` with the
  template version and a computed compliance score.
- The `EnterpriseComplianceValidator` verifies that every generated script comes from an approved
  template and meets the minimum compliance threshold (usually 80%).
- Compliance summaries are exported to `analytics.db` so auditors can trace which
  templates were used and whether any corrective actions occurred. When a
  placeholder or correction is detected, an entry is added to
  `todo_fixme_tracking`. Once resolved, a matching record in `correction_logs`
  links the change to the updated compliance score. This ensures every placeholder
  removal is measurable and auditable.
Example query to list unresolved placeholders:
```sql
SELECT item_id, file_path FROM todo_fixme_tracking WHERE resolved = 0;
```
Mark a placeholder as resolved:
```sql
UPDATE todo_fixme_tracking
SET resolved = 1,
    resolved_timestamp = CURRENT_TIMESTAMP
WHERE item_id = ?;
```


The Flask dashboard exposes a `/dashboard/compliance` endpoint that reads these
metrics and shows real-time placeholder removal progress. When a placeholder is corrected, record the update in `analytics.db:correction_logs`. This ensures future audits can cross-reference removed placeholders with generated fixes.

### Placeholder Correction Workflow
1. Run `scripts/code_placeholder_audit.py --cleanup` to audit and automatically remove flagged placeholders.
2. Review `dashboard/compliance` for updated metrics.
3. If manual fixes were applied, re-run `scripts/code_placeholder_audit.py --update-resolutions`.
4. Record finalized corrections with `scripts/correction_logger_and_rollback.py`.
5. Monitor `/dashboard/compliance` to verify the compliance score improves and database sizes stay under **99.9 MB**.

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

## 6. Database Initialization & Migration
- Initialize all databases with `scripts/database/unified_database_initializer.py`.
- To add new analytics tables run `scripts/database/add_code_audit_log.py` then
  execute any SQL files in `databases/migrations/` such as
  `add_code_audit_log.sql`, `add_correction_history.sql`, and `add_code_audit_history.sql` using `sqlite3` or your preferred migration tool.
  The `correction_history` table stores cleanup events with `user_id`, session ID, file path, action, timestamp, and optional details. The `code_audit_history` table records audit entries with the responsible user and timestamp. Run the migrations if these tables are missing.
  Use `utils.log_utils.ensure_tables()` to verify tables exist and `insert_event()` to write analytics entries.
- After every migration, run `scripts/database/size_compliance_checker.py` to
  verify the 99.9 MB limit is maintained.

### Correction History Table
Use `add_correction_history.sql` to create the `correction_history` table. Each
entry records the `user_id`, session ID, file path, action taken, and timestamp
for code fixes. Verify creation with:
```bash
sqlite3 databases/analytics.db ".schema correction_history"
```

### Code Audit History Table
Use `add_code_audit_history.sql` to create the `code_audit_history` table. This table logs each audit entry along with the user who made the change and the timestamp. Verify creation with:
```bash
sqlite3 databases/analytics.db ".schema code_audit_history"
```

## Database-First Enforcement
The helper `database_first.ensure_db_reference()` verifies a target file path exists in `production.db` before it can be modified. Validation scripts such as `enterprise_dual_copilot_validator.py` flag modules that change files without calling this helper. Always call `ensure_db_reference()` prior to any filesystem write operations.

## 7. End‑to‑End Workflow Example

The following sequence demonstrates how to set up the databases, ingest assets,
audit the results and perform a rollback if necessary. Commands assume
`GH_COPILOT_WORKSPACE` points to the repository root and
`GH_COPILOT_BACKUP_ROOT` is configured outside the workspace.

1. **Initialize the Databases**

   ```bash
   python scripts/database/unified_database_initializer.py
   ```

   Expected output:

   ```text
   [INIT] Created production.db and analytics.db
   [INIT] Verified schema version
   ```

2. **Ingest Template, Documentation, HAR, and Shell Log Assets**

   ```bash
   python scripts/database/template_asset_ingestor.py --workspace "$GH_COPILOT_WORKSPACE" --templates-dir templates
   python scripts/database/documentation_ingestor.py --workspace "$GH_COPILOT_WORKSPACE" --docs-dir docs
   python scripts/database/har_ingestor.py --workspace "$GH_COPILOT_WORKSPACE" --har-dir logs
   python scripts/database/shell_log_ingestor.py --workspace "$GH_COPILOT_WORKSPACE" --logs-dir logs
   ```

   These commands record ingestion events in `analytics.db` and log progress to
   `dashboard/compliance/metrics.json`. Duplicate files are skipped based on
   their content hash, and documentation assets automatically increment a
   `version` field whenever their contents change.

3. **Validate Ingested Assets**

   ```bash
   python scripts/database/ingestion_validator.py --db databases/production.db
   ```

   On success the script prints `{"status": "validated"}` and updates the
   dashboard at `/dashboard/compliance`.

4. **Run the Placeholder Audit**

   ```bash
   python scripts/code_placeholder_audit.py --cleanup --dashboard-dir dashboard/compliance
   ```

   The output includes a summary such as `{"placeholders_removed": 3}` and the
   dashboard reflects the new compliance score. A summary file is also written to
   `dashboard/compliance/placeholder_summary.json` containing the latest
   finding counts, resolutions, and compliance score. See the schema in
   [dashboard/README.md](../dashboard/README.md#placeholder_summaryjson-schema).

5. **Rollback a Problematic Entry**

   ```bash
   python scripts/correction_logger_and_rollback.py --rollback-last
   ```

   When a rollback occurs, the script confirms with
   `{"rollback": true}` and inserts a record into
   `analytics.db:correction_history`.

Open `http://localhost:5000/dashboard/compliance` in your browser to review the
metrics after each step. This endpoint surfaces ingestion counts, placeholder
removal stats and rollback events in real time.

## Recovery Steps

If a synchronization run fails or databases become inconsistent:

1. Stop any running synchronization processes using `DatabaseSynchronizationEngine.stop_realtime_sync`.
2. Restore the last known good backups from the external backup directory referenced by `GH_COPILOT_BACKUP_ROOT`.
3. Re-run `DatabaseSynchronizationEngine.sync` with the restored databases to ensure alignment.
4. Verify `logs/synchronization.log` for any conflict or error entries and address them before resuming automated sync.
