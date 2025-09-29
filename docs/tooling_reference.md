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
| `python scripts/har_ingest.py <file.har> [--db <db>]` | HAR ingestion pipeline (DRY_RUN by default, APPLY persists to SQLite) | `DRY_RUN=0 python scripts/har_ingest.py trace.har --db databases/har_ingest.db` |
| `python tools/validate_fences.py <paths...>` | Validate Markdown code fences (language tags, closures, nested fences) | `python tools/validate_fences.py --strict-inner docs/` |
| `python -m semgrep --config semgrep_rules/` | Optional local semgrep scan using project rules | `python -m semgrep --config semgrep_rules/` |
| `pre-commit run --all-files` | Run all local hooks (ruff, fences, large-file blocker) | `pre-commit run --all-files` |
| `python tools/precommit_block_large.py .codex/*` | Manually block large generated files under `.codex/` | `python tools/precommit_block_large.py .codex/change_log.md` |
