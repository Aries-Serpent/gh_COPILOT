# Enterprise Asset Database Maintenance Guide

The `enterprise_assets.db` database stores consolidated scripts, documentation, and template assets. Use the following commands to recreate or update the database.

```bash
# 1. Initialize the database (creates tables if missing)
python -m scripts.database.unified_database_initializer

# 2. Migrate data from all source databases listed in CONSOLIDATED_DATABASE_LIST.md
python -m scripts.database.unified_database_migration --workspace . \
  $(grep '^-' documentation/CONSOLIDATED_DATABASE_LIST.md | cut -d' ' -f2 | grep -v 'enterprise_assets.db')

# 3. Ingest documentation and templates
python -m scripts.database.documentation_ingestor --workspace .
python -m scripts.database.template_asset_ingestor --workspace .

# 4. Verify database sizes remain under 99.9 MB
python -m scripts.database.size_compliance_checker databases
```

These utilities ensure `enterprise_assets.db` stays synchronized and compliant.
