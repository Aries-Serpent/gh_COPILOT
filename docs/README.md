# Documentation Metrics Validation

This folder contains helper documentation for keeping repository metrics in sync.

## Updating Metrics

Run `python scripts/generate_docs_metrics.py` to refresh metrics in the main
`README.md` and under `documentation/generated/`. The script queries
`production.db` for the current number of tracked scripts and templates and counts
database entries from `documentation/DATABASE_LIST.md`. Use the
`--db-path` option to specify an alternate database file if needed.

## Validation

After updating documentation, execute
`python scripts/validate_docs_metrics.py`. The validator compares the numbers in
`README.md`, `documentation/generated/README.md`, and the technical whitepaper
against the real database values. Pass `--db-path` to override the database
location. The command exits with an error if any values are inconsistent.

This workflow ensures that documentation statistics accurately reflect the
contents of the production database.

## Resetting Benchmark Baselines

Benchmark results are stored in ``benchmark_metrics.db``. Remove this file to
clear previous baselines. The next call to ``benchmark()`` will generate a new
baseline entry.


## Additional Guides
See [DATABASE_FIRST_USAGE_GUIDE.md](DATABASE_FIRST_USAGE_GUIDE.md) for database-first workflow details.
For upcoming work items, refer to [DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md](DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md).
