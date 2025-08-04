# Template Engine

The template engine combines database patterns with lessons learned templates.
Lesson templates are returned by `get_lesson_templates()` in
`learning_templates.py` and merged by `TemplateAutoGenerator` during
initialization and ranking. To extend behavior, add new entries to the lesson
store and they will influence template generation automatically.

`TemplateWorkflowEnhancer` can generate in-memory compliance summaries via
`generate_compliance_report`, combining clustering, pattern mining and
compliance scoring for downstream analytics.
