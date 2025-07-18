# Compression-First Database Migration

The `complete_consolidation_orchestrator.py` script prioritizes compression before moving large tables into the consolidated `enterprise_assets.db` database. Tables exceeding 50,000 rows are exported to CSV and archived with 7z prior to migration. This approach keeps the target database lean and preserves historical records in the `archives/table_exports` folder.

Selective migration ensures only existing source databases are processed. Each migration run checks `analytics.db`, `documentation.db`, and `template_completion.db` in the workspace `databases/` directory and skips any that are missing.
