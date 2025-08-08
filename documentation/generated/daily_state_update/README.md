# Daily State Update

This directory holds generated daily state update reports and related artifacts.

## Verification steps

The following steps were performed to ensure the latest artifacts are available:

1. `git lfs fetch -I documentation/generated/daily_state_update`
2. `git lfs checkout documentation/generated/daily_state_update`
3. Confirmed `gh_COPILOT_Project_White‑Paper_Blueprint_(2025-08-06).pdf` is a PDF via `file`.
4. The conversion workflow fails if any tracked file remains a pointer after checkout.

## Generating new reports

Run `python rename_files_with_spaces.py` after adding a new daily PDF. The script:

1. Renames any files with spaces to use underscores.
2. Converts each PDF to a Markdown file using `tools/convert_daily_whitepaper.py` (or pass `--pdf-file` for a single report).
3. Updates `documentation/generated/daily_state_index.md` so both formats are linked.

CI includes a regression check to ensure the most recent date has both `.pdf` and `.md` files.

To run the conversion manually without renaming, use:

```
make convert-daily-whitepaper
```

