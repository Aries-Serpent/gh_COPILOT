# Template Engine

The template engine combines database patterns with lessons learned templates.
Lesson templates are returned by `get_lesson_templates()` in
`learning_templates.py` and merged by `TemplateAutoGenerator` during
initialization and ranking. To extend behavior, add new entries to the lesson
store and they will influence template generation automatically.

`pattern_mining_engine.rank_patterns_quantum` can rank mined patterns against a
target string using quantum-inspired scoring, enabling adaptive template
selection when quantum modules are available.

`TemplateWorkflowEnhancer` can generate in-memory compliance summaries via
`generate_compliance_report`, combining clustering, pattern mining and
compliance scoring for downstream analytics. Reports include remediation
recommendations and deliver metrics to the dashboard while respecting
monitoring signals to defer heavy processing during high system load. The
enhancer writes modular reports using a content hash in the filename to avoid
duplicates and logs metadata (template count, compliance score, hash) to
`workflow_events` in `analytics.db`. Re-running the enhancer with unchanged
content reuses the existing report and skips new analytics entries. A
`--dry-run` option is available for validating the process without mutating
dashboard files or analytics.

## Curation Pipeline

`template_curation_pipeline.curate_templates` orchestrates asset ingestion,
pattern mining, KMeans-based template deduplication, and objective similarity
scoring. All steps log results to `analytics.db` for downstream reporting and
compliance metrics.

## Key Components

- **Pattern Mining** (`pattern_mining_engine.py`): Extracts recurring three-word
  patterns from stored templates, logs them to `analytics.db`, and clusters them
  with KMeans. Inertia and silhouette metrics provide quality insights.
- **Template Synchronization** (`template_synchronizer.py`): Runs a KMeans-based
  deduplication step to keep only representative patterns before updating
  databases, ensuring concise, validated syncs.
- **Objective Similarity Scoring** (`objective_similarity_scorer.py`): Compares
  objectives against templates using TF-IDF and cosine similarity, with optional
  quantum or Jaccard measures. Results are recorded in analytics logs for
  downstream use.
