## Codex pytest-cov workflow — 2025-08-16T20:36:54

### Symbolic Model

- Required R = {r1: dev extra includes pytest-cov, r2: docs show `pip install .[dev]`, r3: CI example for `pytest --cov` (non-activated)}

### Actions

- Backup created: pyproject.toml -> /workspace/gh_COPILOT/tools/_codex_backup/20250816_203654/pyproject.toml
- Backup created: README.md -> /workspace/gh_COPILOT/tools/_codex_backup/20250816_203654/README.md
- Backup created: docs/testing.md -> /workspace/gh_COPILOT/tools/_codex_backup/20250816_203654/docs/testing.md
- Backup created: pyproject.toml -> /workspace/gh_COPILOT/tools/_codex_backup/20250816_203654/pyproject.toml
- Wrote file: pyproject.toml
- Added pytest-cov to dev extra.
- Backup created: docs/testing.md -> /workspace/gh_COPILOT/tools/_codex_backup/20250816_203654/docs/testing.md
- Wrote file: docs/testing.md
- Updated testing docs in docs/testing.md
- Wrote file: ci_examples/pytest_cov.yml.disabled
- Wrote NON-ACTIVATED CI example: ci_examples/pytest_cov.yml.disabled

### Gaps & Rationales

- None (G = ∅)

### File Hashes (before → after)

- pyproject.toml: 2d0235c27f5be5c753292b3edffd0f29b5886fd24447ad6747f9125bb1fba75d → 06b4766d3a00e7cb34f5f269acb94e97f94c6e546807f39623183247a4427fc9
- README.md: 4e7a1160d4078d8067d6f1a8a786755fd5d5e99cdb8ecbc4e5a395bb81fa9deb → 4e7a1160d4078d8067d6f1a8a786755fd5d5e99cdb8ecbc4e5a395bb81fa9deb
- docs/testing.md: 5119976d94a2fa08862b6346a5035ce1f16d4acdf0eb8d28384d887dcf53df66 → 4aafcff4d207d47555b30a0275c18d988ef9e2bcb3905db430d0cec0132b15dd
- ci_examples/pytest_cov.yml.disabled: (created if not present)

### Next Steps (Manual)

- If you choose to activate CI, **manually** copy the example into your CI system and review.
- Confirm coverage thresholds and reports as desired.
