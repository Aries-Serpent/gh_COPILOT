# Ruff Documentation Exclusion Change Log

- Run: 2025-08-17 22:55:42 

## Phase 1: Preparation @ 2025-08-17 22:55:42
- Repo root: /workspace/gh_COPILOT
- Ruff config target: pyproject.toml
- Merged extend-exclude => ['.git', '__pycache__', 'archive', 'archives', 'build', 'builds', 'deployment/deployment_package_*/*', 'deployment_package_*', 'databases/*.db', '*.log', 'misc', 'scripts/enterprise/*', 'scripts/optimization/*', 'scripts/quantum_placeholders/*', 'copilot_qiskit_stubs/*', 'db_tools/*', 'enterprise_modules/*', 'quantum_optimizer.py', 'databases/*.db', '*.log', 'recovered_files_*', '*.md', '*.rst', 'README.md']
- Updated pyproject.toml with extend-exclude.
- README.md updated: removed doc-lint commands and added exclusion policy note.
- CONTRIBUTING.md updated: added linting scope.
- Found Ruff reference in: .github/workflows/ci.yml
- Found Ruff reference in: .github/workflows/dashboard-compliance.yml
- Found Ruff reference in: Makefile
- Found Ruff reference in: scripts/ingest_test_and_lint_results.py
- Found Ruff reference in: scripts/compliance_aggregator.py
- Found Ruff reference in: scripts/run_checks.py
- Found Ruff reference in: scripts/optimization/enterprise_template_compliance_enhancer.py
- Found Ruff reference in: scripts/utilities/flake8_corrector_base.py
- Found Ruff reference in: scripts/database/database_driven_ruff_corrector.py
- Found Ruff reference in: scripts/database/database_first_correction_engine.py
- Found Ruff reference in: scripts/reporting/generate_compliance_and_test_reports.py
- Found Ruff reference in: README.md
- Found Ruff reference in: CONTRIBUTING.md
- Scanned GH Actions for Ruff references (no modifications applied).
  NOTE: DO NOT ACTIVATE ANY GitHub Actions files. Review manually if needed.
- Ruff check exited with code 2. See 'ruff_output.txt' and 'ruff_error.txt'.
- Gaps detected that may require manual review (see list below).
## Finalization
- Updated files: pyproject.toml, README.md, CONTRIBUTING.md
- Gaps requiring manual follow-up:
  - Unable to read scripts/__pycache__/__init__.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/__pycache__/validate_docs_metrics.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/__pycache__/docs_metrics_validator.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/__pycache__/run_migrations.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/__pycache__/correction_logger_and_rollback.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/validation/__pycache__/secondary_copilot_validator.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/database/__pycache__/add_rollback_strategy_history.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/database/__pycache__/__init__.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/database/__pycache__/add_rollback_logs.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/database/__pycache__/size_compliance_checker.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
  - Unable to read scripts/database/__pycache__/add_violation_logs.cpython-312.pyc: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte

**Symbolic Check:** Target set T' = T \ E, where E = {*.md, *.rst, README.md}.
Config now ensures Ruff excludes E globally via `extend-exclude`.


- Manual adjustment: restored pyproject.toml formatting and re-applied doc exclusions.
