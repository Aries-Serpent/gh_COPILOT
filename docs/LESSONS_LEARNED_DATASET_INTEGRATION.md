# Lessons Learned Dataset Integration

The template generation pipeline now queries the curated `enhanced_lessons_learned` dataset before building templates. During `TemplateAutoGenerator` initialization, lessons are loaded from `databases/learning_monitor.db` and logged using the lessons integrator utilities. The lesson descriptions are combined with existing patterns and templates to guide synthesis.

The validator at `scripts/validation/lessons_learned_integration_validator.py` includes a compliance check that ensures the dataset is present and non-empty, confirming that historical insights inform template generation.

## Lessons Metrics

Integration health is tracked in `databases/analytics.db` within the
`integration_score_calculations` table. The `IntegrationScoreCalculator`
stores the latest `integration_status` value, which the enterprise dashboard
reads to report the lessons integration status. When the analytics database
is empty or missing, the dashboard now reports `NO_DATA` or `PENDING`
depending on whether lessons exist in `learning_monitor.db`.
