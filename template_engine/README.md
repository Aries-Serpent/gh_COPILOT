# Template Engine

The template engine combines database patterns with lessons learned templates.
Lesson templates are returned by `get_lesson_templates()` in
`learning_templates.py` and merged by `TemplateAutoGenerator` during
initialization and ranking. To extend behavior, add new entries to the lesson
store and they will influence template generation automatically.

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
