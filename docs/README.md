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
Consult [DATABASE_QUERY_GUIDE.md](DATABASE_QUERY_GUIDE.md) for examples on querying the databases before implementing new features.
The `template_engine.auto_generator` module clusters stored patterns using KMeans and can return representative templates for automation tasks.

For validation details see [validation/Database_First_Validation.md](validation/Database_First_Validation.md). Copilot-specific notes are available under [.github/docs/Database_First_Copilot.md](../.github/docs/Database_First_Copilot.md).

## Quantum Template Generation

The `docs/quantum_template_generator.py` script demonstrates the production
workflow for generating documentation templates using quantum-inspired scoring.
It queries `production.db` for representative templates with
`TemplateAutoGenerator`. When quantum components are available, the script ranks
templates via `QuantumExecutor`; otherwise a classical fallback score is used.
Run the script with `python docs/quantum_template_generator.py` to produce
scored templates. The underlying `TemplateAutoGenerator` clusters templates
using `sklearn.cluster.KMeans` and exposes a
`get_cluster_representatives()` method for retrieving the best pattern from each
cluster.

### Error Handling

All public APIs under ``template_engine`` raise standard Python exceptions on
invalid input. Database operations log errors to ``analytics.db`` and emit
warnings via ``logging``. Consumers should wrap calls in ``try``/``except``
blocks and consult the logs for detailed context.

### Template Workflow Enhancer

The module ``template_engine.workflow_enhancer`` provides the
``TemplateWorkflowEnhancer`` class for advanced template workflow
optimisation. It clusters stored templates, mines common patterns and writes
a compliance report to ``dashboard/compliance``. Use
``enhance()`` to process a database of templates and generate metrics.
