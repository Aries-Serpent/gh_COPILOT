DRY_RUN Analysis: codex_* scripts
=================================

Scope
- Files: `codex_patch_runner.py`, `codex_update_runner.py`, `codex_setup.py`, `codex_script.py`
- Location: `archive/copied_codex_codebase/`

Summary of contents
- `codex_patch_runner.py`: offline patch application helper (git apply/patch), status logging to `.codex`, and optional `nox` sessions.
- `codex_update_runner.py`: orchestration around repository updates (pattern similar to patch runner).
- `codex_setup.py` / `codex_script.py`: snapshot-specific bootstrap and entry script patterns.

Applicability to active codebase
- The gh_COPILOT repo now includes `gh_copilot.automation` with `StepCtx` + `run_phases`, guardrails, and a demo runner. Overlapping responsibilities:
  - Patch application and update orchestration are already handled by our automation primitives or via git directly.
  - `nox` and heavy tooling are explicitly out-of-scope here.

Recommendation
- Do not ingest these snapshot scripts. They duplicate capabilities and pull in non-local assumptions (`nox`, extensive patch directories, CI guards already covered elsewhere).

Decision
- Not applicable / no integration improvement. Add to deletion post-plan.

