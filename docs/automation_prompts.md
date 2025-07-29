# Automation Usage

## Setup and Ingestion
```
source .venv/bin/activate
python tools/automation_setup.py
```

## Audit and Issue Creation
```
python scripts/code_placeholder_audit.py
python scripts/code_placeholder_audit.py --update-resolutions
python scripts/correction_logger_and_rollback.py
```
Open the dashboard at `http://localhost:5000/dashboard/compliance` to verify updated metrics.
