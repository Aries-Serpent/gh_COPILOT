# Issue: Harden compliance automation

## Summary
Ensure composite compliance scoring, anti‑recursion guards, correction logging, and lessons‑learned capture run without manual triggers.

## Tasks
- Introduce composite compliance scoring and anti‑recursion guards in compliance scripts.
- Implement correction logging with lessons‑learned capture.
- Add automated tests for each mechanism.

## Acceptance Criteria
- Compliance automation runs unattended with composite scoring and anti‑recursion safeguards.
- Corrections and lessons are logged automatically.
- `ruff` and `pytest` succeed.

## Testing
- `ruff`
- `pytest`

