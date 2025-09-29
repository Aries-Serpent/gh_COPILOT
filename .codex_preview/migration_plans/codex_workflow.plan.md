Source: E:/gh_COPILOT/archive/copied_codex_codebase/codex_workflow.py
Target(s):
- gh_copilot/automation/core.py (docstring examples and notes)

Summary:
- Snapshot defines a scripted orchestration with guardrails (no GH Actions),
  inventory/report writing, and NDJSON error logging. Our automation core now
  provides StepCtx + run_phases with dry-run semantics and NDJSON logging
  helper.

Suggested minimal integration:
- Add a short example to core.py docstring demonstrating constructing phases
  and invoking run_phases (already added).
- Consider a follow-up module gh_copilot/automation/sequencer.py (optional) for
  structured task sequences; defer until core is adopted.

Patch sketch (documentation-only):
  - Expand core.py top-level docstring with an "Examples" section and a note
    on guardrails alignment (no CI activation, dry-run by default).

Apply action:
- Documentation update only. After commit and local checks, delete source file
  from snapshot.

