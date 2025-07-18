# Consolidated Database Inventory

The following SQLite databases remain after merging all analytics and documentation sources:

- enterprise_assets.db
- archive.db
- development.db
- staging.db
- testing.db
- production.db

`database_sync_scheduler.py` reads this file to keep these replicas synchronized with `production.db`. All other databases have been archived following the consolidation campaign.

The unified `enterprise_assets.db` replaces the old `analytics.db`, `documentation.db`, and `template_completion.db` files.
