DRY_RUN Analysis: Snapshot Scripts Batch
=======================================

Directory: archive/copied_codex_codebase/scripts

Observed categories
- Codex orchestration workflows: apply_session_logging_workflow.py, codex_orchestrate.py,
  codex_ready_task_runner.py, run_codex_tasks.py, run_sweep.py, deep_research_task_process.py
  - Depend on snapshot-only modules (codex.*), heavy env setup, or nox.
  - Not applicable to gh_COPILOT automation core.
- Environment/setup helpers: setup.sh, export_env*.py, gpu/, env/
  - Snapshot-specific environment management; conflicts with our guardrails.
- Markdown fence repair: fix_markdown_fences.py, fix_md_fences.py
  - We ingested a local validator at tools/validate_fences.py; repair scripts are redundant.
- Session logging shells: session_logging.sh, session_hooks.sh
  - Snapshot hooks; our logging is minimal NDJSON via gh_copilot.automation.
- Utilities: sbom_cyclonedx.py, init_sample_db.py, torch_policy_check.py
  - Optional/third-party tooling (sbom), or tied to snapshot DBs/torch; out of scope.
- Subdirectories: cli/, deploy/
  - Snapshot-specific CLIs and deployment scripts; out of scope.

Recommendation
- Do not ingest scripts from this directory. We have local equivalents for code fence validation; other scripts are not relevant or exceed scope.

Decision
- Mark `scripts/` directory for PENDING deletion from the snapshot after confirmation.

