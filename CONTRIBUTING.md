# Contributing

Thank you for considering a contribution to gh_COPILOT. Please follow these guidelines:

- Review and follow the [Governance Standards](docs/GOVERNANCE_STANDARDS.md).
- Run `bash setup.sh`, activate the virtual environment, and execute `ruff`, `pytest`, and `tools/pre-commit-lfs.sh` before committing.
- Use conventional commit messages and reference these standards in your pull requests.
- Follow the [Git LFS recovery guide](docs/git_lfs_recovery.md) when restoring large binary files.

## Documentation Workflow Checklist

For daily white-paper updates, ensure the following:

- [ ] PDF named `gh_COPILOT Project White‑Paper Blueprint (YYYY‑MM‑DD).pdf` placed in `documentation/generated/daily state update/`
- [ ] `git lfs install` and `git lfs track "*.pdf"` executed; `.gitattributes` committed
- [ ] `python tools/convert_daily_whitepaper.py` run to create Markdown copy
- [ ] `documentation/generated/daily_state_index.md` updated with links to PDF and Markdown

See `documentation/generated/README.md` for detailed instructions.
