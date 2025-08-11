# Contributing

Thank you for considering a contribution to gh_COPILOT. Please follow these guidelines:

- Review and follow the [Governance Standards](docs/GOVERNANCE_STANDARDS.md).
- Run `bash setup.sh`, activate the virtual environment, and execute `ruff`, `pytest`, and `tools/pre-commit-lfs.sh` before committing.
- Use conventional commit messages and reference these standards in your pull requests.
- Follow the [Git LFS recovery guide](docs/git_lfs_recovery.md) when restoring large binary files.

## Safe `rg` usage for large repositories

Use [`rg`](https://github.com/BurntSushi/ripgrep) carefully to avoid overwhelming the console:

- Limit scope with globs or directory exclusions and cap matches.
  Example:
  ```bash
  set +o pipefail && rg "except\s*:" -g "*.py" --max-count 200 | head
  ```
- Ensure downstream tools read all input. Use `set +o pipefail`, `--no-buffer`, and viewers like `head`, `tail`, or `clw`.
- When truncating output, capture the full results to a temporary log for later review:
  ```bash
  set +o pipefail && rg --no-buffer "TODO" -g "*.py" --max-count 200 \
    | tee /tmp/rg_todo.log | head
  ```

## Documentation Workflow Checklist

For daily white-paper updates, ensure the following:

- [ ] PDF named `gh_COPILOT Project White‑Paper Blueprint (YYYY‑MM‑DD).pdf` placed in `documentation/generated/daily_state_update/`
- [ ] `git lfs install` and `git lfs track "*.pdf"` executed; `.gitattributes` committed
- [ ] `python tools/convert_daily_whitepaper.py` run to create Markdown copy and update the index

See `documentation/generated/README.md` for detailed instructions.
