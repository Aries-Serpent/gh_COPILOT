# Consolidated Database List

## Active Enterprise Databases

- enterprise_assets.db
- archive.db  # Size: 2.57 MB
- development.db  # Size: 2.57 MB
- staging.db  # Size: 22.98 MB
- testing.db  # Size: 2.57 MB
- production.db  # Size: 0.02 MB

enterprise_assets.db is limited to 99.9 MB to comply with enterprise storage policies.

## Generating `enterprise_assets.db`

Use the database initializer and migration utilities to create the unified
database and populate it with existing data:

```bash
python scripts/database/unified_database_initializer.py
python scripts/database/unified_database_migration.py --workspace .
```

`unified_database_migration.py` migrates data from `analytics.db`,
`documentation.db`, and `template_completion.db` by default. Pass additional
database filenames as arguments to migrate other sources.
