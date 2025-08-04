# PR Plan: Automate documentation metrics and CI hooks

## Summary
Link documentation metrics scripts into the CI pipeline to remove manual steps.

## Implementation
- Implement `scripts/documentation_metrics.py` for CI use.
- Configure CI under `.github/` to call the metrics script.
- Add tests verifying metrics output format.

## Testing
- `ruff`
- `pytest`

