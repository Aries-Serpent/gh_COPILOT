Source: E:/gh_COPILOT/archive/copied_codex_codebase/codex_task_sequence.py
Target(s):
- gh_copilot/automation/sequencer.py (new, optional)

Summary:
- Snapshot script implements a multi-phase offline task executor with
  environment capture and deterministic seeding. It pulls in optional heavy
  deps (numpy/torch) and writes provenance.

Suggested integration (deferred):
- Introduce a light-weight sequencer that composes StepCtx and provides
  optional dependency flags without importing heavy modules by default.
- Expose only stdlib; advanced integrations with numpy/torch are out-of-scope
  for the core project and can be addressed later behind feature flags.

Patch sketch:
- Create gh_copilot/automation/sequencer.py with a small class that accepts a
  list of StepCtx and runs with shared context and deterministic seed helper
  (stdlib random only), no external deps.

Apply action:
- Defer APPLY until core usage patterns settle; record as intentional
  follow-up in docs/codex_integration_leftovers.md if not implemented soon.

