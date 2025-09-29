Automation Core Onboarding
==========================

Overview
- The `gh_copilot.automation` package provides a small, stdlib-only core for
  orchestrating repository automation via composable phases.
- It follows DRY_RUN by default. APPLY steps must be explicit, and guardrails
  prevent risky changes (e.g., editing `.github/workflows`).

Key Modules
- `gh_copilot.automation.core` — `StepCtx`, `run_phases`, `ExecutionResult`, `RunArtifacts`.
- `gh_copilot.automation.guardrails` — CI guard, backup recursion guard, and forbidden path checks.
- `gh_copilot.automation.exec` — local-only `run_cmd` wrapper that blocks network tools.
- `gh_copilot.automation.logging` — append NDJSON records atomically.

Dry-Run vs Apply
- DRY_RUN=1 (default): no destructive actions, use preview locations when applicable.
- APPLY=1: perform changes; run guardrails before risky operations.

Demo
- Run: `python scripts/demo_automation_run.py` (uses DRY_RUN unless `DRY_RUN=0`).
- Writes a single NDJSON entry to `.codex/action_log.ndjson`.

Snapshot Adapter
- `gh_copilot.compat.codex_snapshot_adapter` can import helpers from a local
  snapshot when `GH_COPILOT_USE_CODEX_SNAPSHOT=1`.

Next Steps
- If desired, add a light `sequencer.py` to build on `StepCtx` for more complex
  task graphs, keeping stdlib-only guarantees.

