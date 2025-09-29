Local test execution notes
-------------------------

- The full repository test suite depends on database migrations and other
  systems; running `pytest -q` locally triggered environment-level errors.
- Minimal tests added for the automation core and guardrails should be
  validated in isolation once the global test fixture behavior is adjusted.
- When ready, run:
  - `python -m ruff check .` (if installed)
  - `python -m pytest -q tests/test_automation_core.py tests/test_guardrails.py`

