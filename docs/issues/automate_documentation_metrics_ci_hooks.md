# Issue: Automate documentation metrics and CI hooks

## Summary
Remove manual steps by linking documentation metrics scripts to the continuous integration pipeline.

## Tasks
- Create or update `scripts/documentation_metrics.py` to emit metrics during CI.
- Add CI configuration under `.github/` to run the metrics script.
- Write tests verifying metrics output format.

## Acceptance Criteria
- CI pipeline runs documentation metrics automatically.
- Metrics script outputs validated format.
- `ruff` and `pytest` succeed.

## Testing
- `ruff`
- `pytest`

