# Compression-First Database Migration

The `complete_consolidation_orchestrator.py` script prioritizes compression before moving large tables into the consolidated `enterprise_assets.db` database. Tables exceeding 50,000 rows are exported to CSV and archived with 7z prior to migration. This approach keeps the target database lean and preserves historical records in the `archives/table_exports` folder.

Beginning with version 4.0, database files larger than **99.9 MB** are first backed up to `/temp/gh_COPILOT_Backups/database_backups` using 7z with maximum compression. Files exceeding **100 MB** are archived and skipped during migration, with the original removed after backup.

Selective migration ensures only existing source databases are processed. Each migration run checks `analytics.db`, `documentation.db`, and `template_completion.db` in the workspace `databases/` directory and skips any that are missing.

## Command-Line Options
The script accepts the following command-line arguments:
- `--source-dir`: Path to the directory containing the source databases (default: `databases/`).
- `--archive-dir`: Path to the directory where archived tables will be stored (default: `archives/table_exports/`).
- `--compression-level`: Compression level for 7z (default: 5).
- `--log-file`: Path to the log file for recording migration details (default: `migration.log`).

### Example
Use a higher compression level to maximize archive reduction:

```bash
python scripts/database/complete_consolidation_orchestrator.py \
    --compression-level 7
```

## Prerequisites
- Python 3.8 or higher.
- The `7z` utility must be installed and available in the system's PATH.
- Sufficient disk space for temporary CSV files and archives.

## Expected Runtime
The runtime depends on the size and number of tables being processed. For example:
- Small databases (<100 MB): ~5 minutes.
- Medium databases (100 MB - 1 GB): ~15-30 minutes.
- Large databases (>1 GB): ~1 hour or more.

## Error Handling
If the migration fails:
- Check the log file (`migration.log`) for error messages.
- Ensure that the `7z` utility is installed and functioning correctly.
- Verify that the source databases exist in the specified directory.
- Ensure there is sufficient disk space for temporary files and archives.
- Retry the migration with the `--log-level debug` option for more detailed output.
