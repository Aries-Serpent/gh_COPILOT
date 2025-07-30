# Automated Ingestion and Audit Prompts

Use the following prompts to operate the automated setup and auditing workflow:

## Initialize Environment and Ingest Assets
```
source .venv/bin/activate
export GH_COPILOT_WORKSPACE=/path/to/gh_COPILOT
export GH_COPILOT_BACKUP_ROOT=/external/backups
python scripts/autonomous_setup_and_audit.py
```
This command initializes missing databases, ingests documentation and template assets, and performs the placeholder audit.

## Run Code Audit and Summarize Findings
```
python scripts/autonomous_setup_and_audit.py
```
The script logs progress using visual indicators and writes results to `dashboard/compliance`.

## Create GitHub Issues from Audit Results
```
python scripts/code_placeholder_audit.py --workspace $GH_COPILOT_WORKSPACE \
    --analytics-db databases/analytics.db \
    --production-db databases/production.db \
    --dashboard-dir dashboard/compliance
```
Audit summaries can be copied to new GitHub issues referencing affected modules.

## Automated Placeholder Cleanup
```bash
python scripts/code_placeholder_audit.py --workspace $GH_COPILOT_WORKSPACE \
    --analytics-db databases/analytics.db --production-db databases/production.db \
    --dashboard-dir dashboard/compliance --cleanup
```
This command audits, cleans placeholders, logs corrections, and updates metrics.

## Mark Corrections and Verify
```bash
python scripts/code_placeholder_audit.py --update-resolutions
python scripts/correction_logger_and_rollback.py
```
Open `/dashboard/compliance` in your browser to confirm all placeholders have been resolved.
