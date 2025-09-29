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

HAR Ingestion
-------------
- Script: `scripts/har_ingest.py`
  - Phases: Validate → JSON schema check → Normalize → Persist (APPLY only) → Emit metrics
  - DRY_RUN=1 (default): simulates writes, prints a compact JSON summary, and logs an NDJSON metric to `.codex/action_log.ndjson`.
  - APPLY (set `DRY_RUN=0`): enables guardrails and persists normalized entries into SQLite (default `databases/har_ingest.db`).
- Guardrails: blocks edits to `.github/workflows`, forbids writing to `C:/temp`/`E:/temp`, and enforces no-recursive-backup patterns before persisting.
- Usage examples:
  - Dry run: `python scripts/har_ingest.py path/to/file.har`
  - Apply: PowerShell `$env:DRY_RUN='0'; python scripts/har_ingest.py path/to/file.har --db databases/har_ingest.db`
           Bash `DRY_RUN=0 python scripts/har_ingest.py path/to/file.har --db databases/har_ingest.db`

Cookbook — StepCtx Patterns
---------------------------
- Shared context:
```python
ctx = {"prepared": False}
def prepare(dry_run: bool = True): ctx["prepared"] = True
def act(): assert ctx["prepared"]
phases = [StepCtx("Prepare","",prepare), StepCtx("Act","",act)]
run_phases(phases, dry_run=True)
```
- Skip in dry-run:
```python
def apply(): ...
run_phases([StepCtx("Apply","",apply,dry_run_ok=False)], dry_run=True)
```

Exec & Adapter Notes
--------------------
- Local Exec allowlist (examples): `python`, `git`, `sqlite3` — network tools like `curl`/`wget` are denied by default in `automation.exec`.
- Snapshot adapter: set `GH_COPILOT_USE_CODEX_SNAPSHOT=1` to enable optional imports of local snapshot helpers (no network); otherwise live automation modules are used. Example:
```python
from gh_copilot.compat.codex_snapshot_adapter import initialize_adapter
mods = initialize_adapter(log_path='.codex/action_log.ndjson')
```

Guardrails Flags
----------------
- `GUARD_DENYLIST` (optional): comma/semicolon-separated absolute path prefixes to block writes (in addition to built-ins like `C:/temp`, `E:/temp`). Used by `validate_no_forbidden_paths`.

Error Handling
--------------
- If a step raises, `run_phases` captures the exception, marks the step log with an `error`, sets `ok=False` overall, and continues to subsequent steps to maximize coverage (useful in DRY_RUN).
- Example:
```python
def boom():
    raise ValueError('boom')
result = run_phases([StepCtx('Boom','',boom)], dry_run=True)
assert result.ok is False
assert result.logs[0]['error']
```
