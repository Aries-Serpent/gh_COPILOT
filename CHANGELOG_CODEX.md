# Codex Change Log (2025-08-21)
- Added `pyotp>=2,<3` to `requirements-test.txt` ensuring TOTP tests have dependency.
- Guarded FastAPI usage in tests with `pytest.importorskip` to avoid ImportError when FastAPI is absent.
- Normalized README links, marking unresolved references with `[MISSING_REF:...]`.
- Logged setup migration `ModuleNotFoundError` in `research_questions.md`.

## Pruned Paths
- Skipped automated repository copy in `codex_task_runner.py` due to disk-space limits; performed manual edits instead.
