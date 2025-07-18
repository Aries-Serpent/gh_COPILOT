# Consolidated Database Inventory

The following SQLite databases remain after merging all analytics and documentation sources:

- enterprise_assets.db
- archive.db
- development.db
- staging.db
- testing.db
- production.db

`database_sync_scheduler.py` reads this file to keep these replicas synchronized with `production.db`. 
All other databases have been archived following the consolidation campaign.

The unified `enterprise_assets.db` replaces `analytics.db`, `documentation.db`, and `template_completion.db`.

**Note:** Initial attempt on 2025-07-18 exceeded the 99.9 MB limit. 
Cleanup involved removing redundant data and compressing tables to reduce the database size. 
The migration succeeded, but the resulting database remains untracked due to size constraints, 
and the lack of an immediate need for tracking. 
Future migrations should evaluate whether tracking this database is necessary, 
and consider additional cleanup or optimization steps if required.
