# Automated Ingestion and Audit Prompts

Follow these sequential steps to configure the environment, ingest assets, run audits, generate code and, if needed, roll back changes.

> **Note:** Quantum features referenced in these prompts operate in placeholder simulation mode. No hardware access is required.

## 1. Database Setup
```bash
source .venv/bin/activate
export GH_COPILOT_WORKSPACE=/path/to/gh_COPILOT
export GH_COPILOT_BACKUP_ROOT=/external/backups  # must be outside the workspace
python scripts/database/unified_database_initializer.py
```
- ensure the backup root resides outside `GH_COPILOT_WORKSPACE`; internal paths are rejected.

Expected output:
```text
[INIT] Created production.db and analytics.db
```
Troubleshooting:
- *permission denied*: verify both paths exist and are writable.
- *database is locked*: close other processes using the database files.

## 2. Asset Ingestion
```bash
python scripts/autonomous_setup_and_audit.py --ingest-only
```
Internally this calls [`scripts/database/documentation_ingestor.py`](../scripts/database/documentation_ingestor.py) and [`scripts/database/template_asset_ingestor.py`](../scripts/database/template_asset_ingestor.py).
Expected output:
```text
[INGEST] 20 docs loaded
[INGEST] 15 templates loaded
```
Duplicate files are skipped automatically based on their content hash.
Troubleshooting:
- *0 files found*: confirm Markdown files exist under `docs/` and `prompts/`.

## 3. Audit
```bash
python scripts/code_placeholder_audit.py --dashboard-dir dashboard/compliance
```
Expected output:
```text
{"placeholders_removed": 3}
```
Troubleshooting:
- *invalid path*: ensure `GH_COPILOT_WORKSPACE` is set before running the audit.

## 4. Code Generation
```bash
python template_engine/db_first_code_generator.py --db databases/production.db --out generated/
```
Expected output:
```text
[GENERATE] wrote generated/example.py
```
Troubleshooting:
- *ModuleNotFoundError: sklearn*: run `bash setup.sh` to install missing dependencies.

## 5. Rollback
```bash
python scripts/correction_logger_and_rollback.py --rollback-last
```
Expected output:
```text
{"rollback": true}
```
Troubleshooting:
- *No entry found*: confirm at least one record exists in `analytics.db:correction_history`.
