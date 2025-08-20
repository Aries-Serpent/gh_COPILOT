# Tooling Reference

This document lists commonly used command-line scripts in the **gh_COPILOT** repository.

| Script | Purpose | Example |
| --- | --- | --- |
| `python scripts/run_checks.py` | Run Ruff, Pyright, and pytest sequentially. | `python scripts/run_checks.py` |
| `python scripts/docs_status_reconciler.py` | Generate `docs/task_stubs.md` and `docs/status_index.json` from phase task metadata. | `python scripts/docs_status_reconciler.py` |
| `python -m scripts.compliance_score_cli` | Print the latest compliance score as JSON. | `python -m scripts.compliance_score_cli` |
| `python scripts/wlc_session_manager.py --session-id <id>` | Log session completion with environment validation. | `python scripts/wlc_session_manager.py --session-id 12345` |
| `python scripts/run_tests_safe.py` | Run pytest with optional coverage and JSON reporting. | `python scripts/run_tests_safe.py` |
| `python scripts/generate_docs_metrics.py` | Build documentation metrics. | `python scripts/generate_docs_metrics.py` |
| `python -m scripts.docs_metrics_validator` | Validate documentation metrics using the SecondaryCopilotValidator. | `python -m scripts.docs_metrics_validator` |
| `bash scripts/lfs_full_repair.sh` | Perform full Git LFS repair and history migration. | `bash scripts/lfs_full_repair.sh` |
| `sh scripts/lfs_restore.sh` | Simulate restoring Git LFS pointers. | `sh scripts/lfs_restore.sh` |
| `bash scripts/deploy_dashboard.sh <env>` | Deploy the dashboard to the specified environment. | `bash scripts/deploy_dashboard.sh production` |

