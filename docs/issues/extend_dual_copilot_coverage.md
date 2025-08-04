# Issue: Extend dual‑Copilot coverage

## Summary
Integrate the secondary validator into all wrappers and orchestration scripts, addressing failing modules in documentation, template caching, session management, and compliance metrics.

## Tasks
- Audit wrappers and orchestrators for missing `SecondaryCopilotValidator` calls.
- Add secondary validation where absent.
- Expand tests under `tests/` to exercise validation paths.

## Acceptance Criteria
- Every wrapper and orchestrator invokes `SecondaryCopilotValidator`.
- Updated tests cover dual‑Copilot paths and pass.
- `ruff` and `pytest` run cleanly.

## Testing
- `ruff`
- `pytest`

