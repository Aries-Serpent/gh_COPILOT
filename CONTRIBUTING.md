# Contributing

Thank you for considering a contribution to gh_COPILOT. Please follow these guidelines:

- Review and follow the [Governance Standards](docs/GOVERNANCE_STANDARDS.md).
- Run `bash setup.sh`, activate the virtual environment, and execute `ruff`, `pytest`, and `tools/pre-commit-lfs.sh` before committing.
- Ruff checks Python source files only; documentation (`*.md`, `*.rst`) is excluded by configuration.
- Use `make compliance` to run `ruff`, `pytest`, and `scripts/code_placeholder_audit.py` in a single step.
- Use conventional commit messages and reference these standards in your pull requests.
- Follow the [Git LFS recovery guide](docs/git_lfs_recovery.md) when restoring large binary files.
- Run helper scripts via module syntax (``python -m scripts.<name>``) instead of
  invoking paths directly. For example, ``python -m scripts.generate_docs_metrics``.

## Safe ripgrep usage for large repositories

Use the wrapper `./tools/safe_rg.sh` to search without flooding the console. It limits line widths, skips heavy directories, and saves full results when matches exceed a safe size.

- **Limit scope** with globs or directory exclusions and cap matches (default 200 via `SAFE_RG_MAX_COUNT`):
  ```bash
  set +o pipefail && ./tools/safe_rg.sh "except\s*:" -g "*.py"
  ```
- **Control downstream consumption** using `set +o pipefail` and viewers like `head`, `tail`, or `clw` to consume the output safely.
- **Diagnostics**: when results are truncated, the script stores the complete output under `$GH_COPILOT_BACKUP_ROOT` and prints the file path for manual review. Adjust the limit with `SAFE_RG_MAX_COUNT` if needed:
  ```bash
  SAFE_RG_MAX_COUNT=100 set +o pipefail && ./tools/safe_rg.sh "TODO" -g "*.py"
  ```

## Documentation Workflow Checklist

For daily white-paper updates, ensure the following:

- [ ] PDF named `gh_COPILOT Project White‑Paper Blueprint (YYYY‑MM‑DD).pdf` placed in `documentation/generated/daily_state_update/`
- [ ] `git lfs install` and `git lfs track "*.pdf"` executed; `.gitattributes` committed
- [ ] `python tools/convert_daily_whitepaper.py` run to create Markdown copy and update the index

See `documentation/generated/README.md` for detailed instructions.


### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0`.
### Optional GUI dependencies

Some legacy GUI tests rely on PyQt6. The test suite first tries to import
the real library and falls back to the lightweight stub in
`tests/stubs/pyqt6.py` when PyQt6 is absent. Install PyQt6 locally if you
wish to exercise the full GUI functionality; otherwise the stub allows
CI to execute these tests without the dependency.
## Linting Scope
- Ruff targets Python files.
- Documentation files (`*.md`, `*.rst`, including `README.md`) are excluded via `extend-exclude`.
