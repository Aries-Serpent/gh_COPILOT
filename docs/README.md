# Documentation Metrics Validation

This folder contains helper documentation for keeping repository metrics in sync.

On every push the CI pipeline automatically runs
`docs/generate_docs_metrics.py`, then `scripts/docs_status_reconciler.py` and
`scripts/validate_docs_metrics.py` to ensure documentation statistics stay
consistent with the production database and to flag status drift. Sessions must
run through `start_session` and `end_session` so successful wrap-ups contribute
to the session success ratio used in the composite compliance score.

## Updating Metrics

Run `python docs/generate_docs_metrics.py` to refresh metrics in the main
`README.md` and under `documentation/generated/`. The script queries
`databases/production.db` for the current number of tracked scripts and templates and counts
database entries from `documentation/DATABASE_LIST.md`. Use the
`--db-path` option to specify an alternate database file if needed. After
regenerating metrics run `python scripts/docs_status_reconciler.py` followed by:
```bash
python -m scripts.docs_metrics_validator
python scripts/wlc_session_manager.py --db-path databases/production.db
```
The session manager records the update in `production.db` and writes a log file under `$GH_COPILOT_BACKUP_ROOT/logs`.

## Validation

After updating documentation, execute
`python -m scripts.docs_metrics_validator`. The validator compares the numbers in
`README.md`, `documentation/generated/README.md`, and the technical whitepaper (`docs/COMPLETE_TECHNICAL_SPECIFICATIONS_WHITEPAPER.md`)
against the real database values. Pass `--db-path` to override the database
location. The command exits with an error if any values are inconsistent. The
alias script `scripts/docs_metrics_validator.py` remains available for legacy
calls.

This workflow ensures that documentation statistics accurately reflect the
contents of the production database.

### Related Requirements
- **Database Maintenance Scheduler:** see [SYSTEM_OVERVIEW.md](../documentation/SYSTEM_OVERVIEW.md#database-synchronization).
- **Validation Helper:** see [DATABASE_FIRST_USAGE_GUIDE.md](DATABASE_FIRST_USAGE_GUIDE.md#database-first-enforcement).
- **Visual Indicator Standards:** see [GITHUB_COPILOT_INTEGRATION_NOTES.md](GITHUB_COPILOT_INTEGRATION_NOTES.md#visual-processing).

## Resetting Benchmark Baselines

Benchmark results are stored in ``benchmark_metrics.db``. Remove this file to
clear previous baselines. The next call to ``benchmark()`` will generate a new
baseline entry.


## Additional Guides
See [DATABASE_FIRST_USAGE_GUIDE.md](DATABASE_FIRST_USAGE_GUIDE.md) for database-first workflow details.
For upcoming work items, refer to [DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md](DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md).
Consult [DATABASE_QUERY_GUIDE.md](DATABASE_QUERY_GUIDE.md) for examples on querying the databases before implementing new features.
The `template_engine.auto_generator` module clusters stored patterns using KMeans and can return representative templates for automation tasks.

- [WORKSPACE_OPTIMIZER.md](WORKSPACE_OPTIMIZER.md) explains how to archive unused files and log optimization metrics.
- [DEPLOYMENT_ORCHESTRATOR.md](DEPLOYMENT_ORCHESTRATOR.md) describes the unified deployment orchestration workflow.
- [timeline_risk_plan.md](timeline_risk_plan.md) provides week-by-week milestones and a risk mitigation plan for disaster recovery, GUI, and the synchronization engine.
- [COMPLIANCE_PIPELINE.md](COMPLIANCE_PIPELINE.md) outlines each stage of the compliance pipeline and the responsibilities for maintaining repository standards.

- [HAR_INGESTION_PIPELINE.md](HAR_INGESTION_PIPELINE.md) documents the phased HAR ingestion pipeline built on `gh_copilot.automation` with DRY_RUN safety and guardrails.

## Docs Editing Checklist

- Validate Markdown fences locally before committing to avoid broken examples:

```bash
python tools/validate_fences.py --strict-inner docs/
```

- Optional local SAST & lint (if installed):

```bash
python -m semgrep --config semgrep_rules/
ruff check .
```

For validation details see [validation/Database_First_Validation.md](validation/Database_First_Validation.md). Copilot-specific notes are available under [.github/docs/Database_First_Copilot.md](../.github/docs/Database_First_Copilot.md).

## Quantum Preparation, Executive Guides, and Certification

- [quantum_preparation/README.md](quantum_preparation/README.md) – steps to prime the toolkit for quantum-enabled features
- [executive_guides/README.md](executive_guides/README.md) – quick references for leadership teams
- [certification/README.md](certification/README.md) – procedures for issuing and validating certificates

## Quantum Template Generation

The `docs/quantum_template_generator.py` script demonstrates the production
workflow for generating documentation templates using quantum-inspired scoring.
It queries `databases/production.db` for representative templates with
`TemplateAutoGenerator`. Quantum components run in simulation mode via
`QuantumExecutor`, and hardware flags are ignored until future integration.
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

### Documentation DB Analyzer

``scripts/database/documentation_db_analyzer`` audits documentation
databases for placeholder gaps and table statistics. Results are recorded in
``analytics.db`` and every run triggers ``SecondaryCopilotValidator`` to
enforce the dual-copilot review pattern.

## Quantum Placeholder Modules

Modules under `scripts/quantum_placeholders/` act as stubs for upcoming
quantum features. Each file sets `PLACEHOLDER_ONLY = True`, and packaging
utilities detect this marker to skip the modules so they are never included
in production builds. Importing them while `GH_COPILOT_ENV` is set to
`"production"` raises a `RuntimeError` via `ensure_not_production`.
They remain importable for experimentation and planning.
Progress on these placeholders and other pending modules is tracked in
[STUB_MODULE_STATUS.md](STUB_MODULE_STATUS.md).


### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
