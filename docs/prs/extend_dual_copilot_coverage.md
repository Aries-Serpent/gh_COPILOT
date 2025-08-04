# PR Plan: Extend dual‑Copilot coverage

## Summary
Integrate `SecondaryCopilotValidator` across wrappers and orchestrators and expand tests for dual‑Copilot paths.

## Implementation
- Audit wrappers/orchestrators for missing secondary validation.
- Add `SecondaryCopilotValidator` checks.
- Update tests to cover validation paths.

## Testing
- `ruff`
- `pytest`

